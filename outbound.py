import spredSheet
import time
import random
import gspread
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
    sheet_name, spredSheetBaseBi = connectInSpredSheetBi()

    # Conecta na planilha somente uma vez
    if spredSheetBaseBi is None or sheet_name is None:
        logger.info(f'Falha ao carregar Planilha de devolução')
        return
    logger.info(f'Planilha {spredSheetBaseBi.title} e {sheet_name} conetados com sucesso')

    # Carrega todos dos dados da planilha devolução em memoria
    logger.info(f'Carregando dados de Devolução')
    datasDevolution = loadAllSheets(spredSheetBaseBi)
    if datasDevolution is None:
        logger.error("Erro ao tentar buscar dados da planilha de devolução")
        return
    logger.info(f'Dados de devolução carregados - OK')

    # Carrega todos os dados da gui BASE_BI_2 em memoria
    logger.info(f'Carregando dados da Base BI')
    datasBaseBi = loadDatasSheetBaseBi(sheetBaseBi=sheet_name)    
    if datasBaseBi is None:
        logger.error("Erro ao tentar buscar dados da Base_BI")
        return
    logger.info(f'Dados da Base BI carregados -> OK')

    # Fitro para somente pendentes
    logger.info(f"Filtrando registros")
    for datas in reversed(datasBaseBi[1:]):
        dateInValue = convertDate(datas[1])

        # valida status (ignora os efetivados)
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
    # logger.warning(filterDatas) 
    # return

    for datas in filterDatas:
        trackingCode = datas[0].strip().upper()
        client = datas[2].strip().upper()

        # Obtém diretamente a aba do cliente
        values = datasDevolution.get(client)
        if not values:
            logger.warning(f"Guia {client} não encontrada para {trackingCode}")
            continue

        logger.info(f"Buscando Devolução {trackingCode} para o Cliente: {client}")

        for line in reversed(values[1:][-500:]):
            codigoRastreio = line[0].strip().upper()
            nfd = line[1].strip().upper()
            dataNfd = line[2].strip().upper()
            
            if  codigoRastreio == trackingCode and nfd != '' and dataNfd != '':
                logger.info(f"Devolução encontrada -> {client}: {codigoRastreio}")
                updateLine(line,sheet_name)
                # if cont >= 10:
                #     time.sleep(10)
                #     cont = 0
                # else:
                #     cont = cont + 1
                break

    logger.info("============ FIM DO PROCESSAMENTO - JOB UPDATE ==================")            

# Calcula tempo de processaomento em dias
def calcProcessTime(dateStr, currentDate):
    try:
        dateIn = datetime.strptime(dateStr,"%d/%m/%Y").date()
        # dateIn = dateStr
        days = (currentDate - dateIn).days
        return days
    except Exception as err:
        logger.exception(f"Erro ao tenta calcular process time -> IN:{dateStr} -> {err}")

# Busca somente os dados da aba Base_BI
def loadDatasSheetBaseBi(sheetBaseBi):
    try:
        # spredSheetDev = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
        # sheetBaseBi = spredSheetDev.worksheet(os.getenv("SHEET_NAME_BASE_BI"))
       
        # pega os dados da planilha BASE_BI
        datasSheetBaseBi = sheetBaseBi.get_all_values()
        return datasSheetBaseBi
    except Exception as err:
        logger.exception(f"Erro ao obter dados da aba {sheetBaseBi} -> {err}")
        return None,None

# Busca todos os dados de devolução de todas as abas
def loadAllSheets(spredSheetDev):
    cache_sheets = {}
    try:
        # spredSheetDev = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
        
        # pega os todos dados da planilha de DEVOLUÇÃO
        for sheet in spredSheetDev:
            cache_sheets[sheet.title] = sheet.get_all_values()
        return cache_sheets
    except Exception as err:
        logger.exception(f"Erro ao tentar obter dados de devolução, {err}")
        return None

def connectInSpredSheetBi():
    try:
        spredSheetBaseBi = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
        sheetBaseBi = spredSheetBaseBi.worksheet(os.getenv("SHEET_NAME_BASE_BI"))
        return sheetBaseBi, spredSheetBaseBi
    except Exception as err:
        logger.error(f"Erro ao tentar conectar na planilha BASE_BI -> {err}")
        return None, None

# Adiciona novo registro na planilha
def addLine(spredSheetStruct,sheet):
    # spredSheetBaseBi = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
    # sheet = spredSheetBaseBi.worksheet(os.getenv("SHEET_NAME_BASE_BI"))
    # Adiciona uma linha no final
    # sheet.append_row(spredSheetStruct)
    retry_google_api(
        sheet.append_row,
        spredSheetStruct
    )

    # Última linha inserida
    last_row = len(sheet.get_all_values())

    # Fórmula na coluna I da linha inserida
    formula = (
        f'=SE(B{last_row}="";"";'
        f'HOJE()-DATA('
        f'DIREITA(B{last_row};4);'
        f'EXT.TEXTO(B{last_row};4;2);'
        f'ESQUERDA(B{last_row};2)))'
    )

    # Coluna H (Status)
    # status = spredSheetStruct[7]
    retry_google_api(
        sheet.update_acell,
        f"I{last_row}",
        formula
    )

    format_cell_range(sheet, f"H{last_row}", vermelho)

    logger.info(f"Devolução rastreio {spredSheetStruct[0]} Incluida com sucesso!!")
    
# Atualiza a linha na BASE_BI
def updateLine(datasDevol,sheetBaseBi):
    status = "EFETIVADO"

    if datasDevol:
        trackingCode = datasDevol[0].strip()
        nfd = datasDevol[1].strip()
        dataNfd = datasDevol[2].strip()
        user = datasDevol[3].strip()
        updateAt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
         
        # try:
        cell = retry_google_api(
            sheetBaseBi.find,
            trackingCode
        )

        if cell:
            retry_google_api(
                sheetBaseBi.batch_update,
                [
                    {
                        "range": f"E{cell.row}:H{cell.row}",
                        "values": [[nfd, dataNfd, user, status]]
                    },
                    {
                        "range": f"J{cell.row}",
                        "values": [[updateAt]]
                    }
                ]
            )
        
            retry_google_api(
                    format_cell_range,
                    sheetBaseBi,
                    f"H{cell.row}",
                    verde
                )
        else:
            logger.error(f"Erro ao tentar atualizar {trackingCode} na planilha")
            raise Exception(f"Erro ao tentar atualizar {trackingCode} na planilha")

    logger.info("Planilha atualizada com sucesso!")


def retry_google_api(func, *args, retries=10, wait=10, **kwargs):

    for tentativa in range(retries):

        try:
            logger.info(
                f"API Connected "
                f"(Retry {tentativa + 1}/{retries})"
            )

            return func(*args, **kwargs)

        except gspread.exceptions.APIError as err:

            # Só trata erro 429
            if err.response.status_code != 429:
                raise

            # Backoff exponencial
            tempo_espera = wait * (2 ** tentativa)

            # Adiciona um pequeno tempo aleatório
            # para evitar várias requisições simultâneas
            jitter = random.uniform(0, 5)

            tempo_espera += jitter
            print(tempo_espera)

            logger.warning(
                f"Quota da API do Google Sheets excedida. "
                f"Tentativa {tentativa + 1}/{retries}. "
                f"Aguardando {tempo_espera:.1f}s..."
            )

            time.sleep(tempo_espera)

    raise Exception(
        f"Google Sheets API: número máximo de tentativas "
        f"({retries}) excedido."
    )