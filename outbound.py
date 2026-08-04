import spredSheet
import time
from datetime import datetime
from dotenv import load_dotenv
import os
from logger import logger
from datetime import datetime, timedelta
from gspread_formatting import CellFormat, Color, format_cell_range
load_dotenv()



verde = CellFormat( backgroundColor=Color(0.0, 0.8, 0.0)) #Verde

vermelho = CellFormat(backgroundColor=Color(1.0, 0.0, 0.0)) # Vermelho

def convertDate(dataHora):
    try:
        dateInValue = datetime.strptime(dataHora.strip(),"%d/%m/%Y").date()
        return dateInValue
    except Exception as err:
        logger.error(f"Campo {dataHora} não poder ser convertido, {err}")
        return None
        
# executa as regras de atualização
def run():
    filterDatas = [] 
    cont = 0
    periodDay = int(os.getenv("DAYS_LIMIT_DEV", "7"))
    limitDate = datetime.now().date() - timedelta(days=periodDay)

    # Carrega todos dos dados da planilha devolução em memoria
    logger.info(f'Carregando dados de Devolução')
    datasDevolution = loadAllSheets()
    if datasDevolution is None:
        logger.error("Erro ao tentar buscar dados da planilha de devolução")
        return
    logger.info(f'Dados de devolução carregados - OK')

    # Carrega todos os dados da gui BASE_BI_2 em memoria
    logger.info(f'Carregando dados da Base BI')
    datasBaseBi = loadDatasSheetBaseBi()    
    if datasBaseBi is None:
        logger.error("Erro ao tentar buscar dados da Base_BI")
        return
    logger.info(f'Dados da Base BI carregados -> OK')

    # Fitro para somente pendentes
    logger.info(f"Filtrando registros")
    for datas in reversed(datasBaseBi[1:]):
        dateInValue = convertDate(datas[1])

        # valida status
        if datas[7].strip().upper() != "PENDENTE":
            continue

        # valida conversão de datas
        if dateInValue is None:
            logger.error(f"{datas[0]}: falha na conversão de datas -> data recebimento: {datas[1]}")
            continue

        # Verifica a data limite
        if dateInValue < limitDate :
            break

        filterDatas.append(datas)

    logger.info(f"{len(filterDatas)} -> adiconados no processamento")

    for datas in filterDatas:
        trackingCode = datas[0].strip().upper()
        client = datas[2].strip().upper()

        # Obtém diretamente a aba do cliente
        values = datasDevolution.get(client)
        if not values:
            logger.warning(f"Guia {client} não encontrada para {trackingCode}")
            continue

        logger.info(f"Buscando devolução. Codigo: {trackingCode} Cliente: {client} ")
        for line in values:
            codigoRastreio = line[0].strip().upper()
            
            if  codigoRastreio == trackingCode:
                logger.info(f"Devolução encontrada na GUIA. {client} -> {codigoRastreio}")
                updateLine(line)

                if cont >= 12:
                    time.sleep(7)
                else:
                    cont = cont + 1

    logger.info("============ FIM DO PROCESSAMENTO - JOB UPDATE ==================")            
# Busca somente os dados da aba Base_BI
def loadDatasSheetBaseBi():
    try:
        spredSheetDev = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
        sheetBaseBi = spredSheetDev.worksheet(os.getenv("SHEET_NAME_BASE_BI"))
        # pega os dados da planilha BASE_BI
        datasSheetBaseBi = sheetBaseBi.get_all_values()
        return datasSheetBaseBi
    except Exception as err:
        logger.exception(f"Erro ao obter dados da aba {sheetBaseBi} -> {err}")
        return None

# Busca todos os dados de devolução de todas as abas
def loadAllSheets():
    cache_sheets = {}
    try:
        spredSheetDev = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
        # pega os todos dados da planilha de DEVOLUÇÃO
        for sheet in spredSheetDev:
            cache_sheets[sheet.title] = sheet.get_all_values()
        return cache_sheets
    except Exception as err:
        logger.exception(f"Erro ao tentar obter dados de devolução, {err}")
        return None

# Adiciona novo registro na planilha
def addLine(spredSheetStruct):
    spredSheetBaseBi = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
    sheet = spredSheetBaseBi.worksheet(os.getenv("SHEET_NAME_BASE_BI"))
    
    # Adiciona uma linha no final
    sheet.append_row(spredSheetStruct)

    # Última linha inserida
    last_row = len(sheet.get_all_values())

    # Coluna H (Status)
    status = spredSheetStruct[7]

    if status == "PENDENTE":
        format_cell_range(sheet, f"H{last_row}", vermelho)
    else:
        format_cell_range(sheet, f"H{last_row}", verde)

    logger.info(f"Devolução rastreio {spredSheetStruct[0]} Incluida com sucesso!!")
    
# Atualiza a linha na BASE_BI
def updateLine(datasDevol):

    spredSheetDev = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
    sheetBaseBi = spredSheetDev.worksheet(os.getenv("SHEET_NAME_BASE_BI"))

    trackingCode = datasDevol[0]
    nfd = datasDevol[1]
    dataNfd = datasDevol[2]
    user = datasDevol[3]
    status = "EFETIVADO"
    updateAt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    try:
        cell = sheetBaseBi.find(trackingCode)

        sheetBaseBi.batch_update([
            {
                "range": f"E{cell.row}:H{cell.row}",
                "values": [[nfd, dataNfd, user, status]]
            },
            {
                "range": f"J{cell.row}",
                "values": [[updateAt]]
            }
        ])

        if status == "Pendente":
            format_cell_range(sheetBaseBi, f"H{cell.row}", vermelho)
        else:
            format_cell_range(sheetBaseBi, f"H{cell.row}", verde)

        logger.info("Planilha atualizada com sucesso!")

    except Exception as e:
        logger.error(f"Código {trackingCode} não encontrado na planilha.-> {e}")