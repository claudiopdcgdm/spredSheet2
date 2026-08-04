import spredSheet
import outbound
import os
from datetime import datetime, timedelta
import time
from logger import logger

# Calcula tempo de processaomento em dias
def calcProcessTime(dateStr, currentDate):
    try:
        # dateIn = datetime.strptime(dateStr,"%d/%m/%Y %H:%M:%S").date()
        dateIn = dateStr
        days = (currentDate - dateIn).days
        return days
    except Exception as err:
        logger.exception(f"Erro ao tenta calcular process time -> IN:{dateStr} -> {err}")

def normalizeDate(data):
    data = data.strip()

    formatos = [
        ("%d/%m/%Y", "%d/%m/%Y"),  # já está no formato correto
        ("%Y-%m-%d", "%d/%m/%Y"),  # converte de yyyy-mm-dd
    ]

    for entrada, saida in formatos:
        try:
            return datetime.strptime(data, entrada).strftime(saida)
        except ValueError:
            continue

    logger.error("Formato de data imcompativel, ajuste os dados da planilha")

def convertDate(dataHoraRecebe):
    try:
        dateInValue = datetime.strptime(dataHoraRecebe.strip(),"%d/%m/%Y %H:%M:%S").date()
        return dateInValue
    except Exception as err:
        logger.exception(f"Campo {dataHoraRecebe} não poder ser convertido, {err}")
        return None

def run(spredSheetId):
    logger.info(f'Carregando dados de Recebimento')

    periodDay = int(os.getenv("DAYS_LIMIT_RECEB", "7"))
    limitDate = datetime.now().date() - timedelta(days=periodDay)
    currentDate = datetime.now().date()
    cont = 0
    filterDatas = []

    logger.info("Conectando na planilha de recebimento")
    spredSheetLoad = spredSheet.loadSpredSheet(spredSheetId)
    if spredSheetLoad is None:
        logger.info("Falha ao tentar acessar planilha de recebimento")
        return

    sheet1 = spredSheetLoad.sheet1
    datas_sheet1 = sheet1.get_all_values()
    logger.info("Carregando dados da planilha de Base BI")
    datasBaseBi = outbound.loadDatasSheetBaseBi()
    if datasBaseBi is None:
        logger.info("Falha ao tentar acessar planilha Base BI")
        return

    # Filtro para pegar periodo configurado
    logger.info(f"Filtrando registros")
    for datas in reversed(datas_sheet1[2:]):
        dateInValue = convertDate(datas[0])

        if dateInValue is None:
            logger.error(f"{data[1]}: Falha ao tentar converter data -> {data[0]}")
            continue

        # Verifica a data limite
        if dateInValue < limitDate:
            break

        filterDatas.append(datas)
        
    logger.info(f"{len(filterDatas)} -> Adicionados ao processamento")

    for data in reversed(filterDatas):
        try:
            logger.info(f"Processando informações de recebimento")
            dateInValue = convertDate(data[0])

            codigoRastreio = data[1]
            transportadora = data[2]
            # dataRecebimento = data[3]
            dataRecebimento = normalizeDate(data[3])
            usuarioReceb = data[5]
            cliente = data[6]

            nfd = None
            dataNfd = None
            usuarioDev = None
            status = "PENDENTE"

            tempoProcessamento = calcProcessTime(dateInValue, currentDate)

            spredSheetStruct = [
                codigoRastreio,
                dataRecebimento,
                cliente,
                transportadora,
                nfd,
                dataNfd,
                usuarioDev,
                status,
                tempoProcessamento,
            ]

            logger.info(f"DADOS LISTA DE INFO: -> {spredSheetStruct}")
            

            # validar se o codigo rastreio jah existe na planilha na BASE
            codigos_base = {
                            linha[0].strip().upper()
                            for linha in datasBaseBi[1:]  # Ignora o cabeçalho
                            if linha and linha[0].strip()
                        }
            if codigoRastreio.strip().upper() in codigos_base:
                logger.info(f"Código de rastreio {codigoRastreio} já inserido na BASE!")

            else:
                outbound.addLine(spredSheetStruct)
                if cont >= 12:
                    time.sleep(7)
                else:
                    cont = cont + 1
    
        except Exception as err:
            logger.exception(f"Erro ao processar a linha {data}: {err}")

    logger.info("============ FIM DO PROCESSAMENTO - JOB RECEBIMENTO ==================")
