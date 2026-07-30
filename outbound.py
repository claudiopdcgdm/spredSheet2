import spredSheet
import time
import os
from datetime import datetime, timedelta
import gspread

def convertDate(dataHora):
    try:
        dateInValue = datetime.strptime(dataHora.strip(),"%d/%m/%Y").date()
        periodDay = int(os.getenv("TIME_UPDATE", "7"))
        limitDate = datetime.now().date() - timedelta(days=periodDay)
        return dateInValue, limitDate
    except Exception as err:
        print(f"Campo {dataHora} não poder ser convertido, {err}")

def loadSpredSheetOutbound(spredSheetId, trackingCode, clienteName):
    spredSheetLoad = spredSheet.loadSpredSheet(spredSheetId)

    time.sleep(8)

    try:
        # Obtém a aba do cliente
        sheet = spredSheetLoad.worksheet(clienteName)

        # Carrega todos os dados apenas uma vez
        sheetDatas = sheet.get_all_values()

        devolStruct = []

        for linha in sheetDatas[1:]:  # Ignora o cabeçalho

            # Verifica se a linha possui todas as colunas necessárias
            if len(linha) < 4:
                continue

            # Compara o código de rastreio
            if linha[0].strip().upper() == trackingCode.strip().upper():

                # REGRA PARA OBTER REGISTROS MAIORES QUE O TEMPO INFORMADO NO TIME_UPDATE
                # dataIn = linha[2].strip()
                # dateInValue, limitDate = convertDate(dataIn)
                # if dateInValue >= limitDate:
                #     devolStruct = [
                #         linha[1],      # NFD
                #         linha[2],      # Data
                #         linha[3],      # Usuário
                #         "EFETIVADO"
                #     ]
                # else:
                #     print("Registro fora do período.")

                devolStruct = [
                    linha[1],      # NFD
                    linha[2],      # Data
                    linha[3],      # Usuário
                    "EFETIVADO"
                ]
                break

        if not devolStruct:
            print(f"Código {trackingCode} não encontrado na aba {clienteName}.")

        return devolStruct

    except gspread.exceptions.WorksheetNotFound:
        print(f"A aba '{clienteName}' não foi encontrada.")
        return []

    except Exception as err:
        print(f"Erro ao ler planilha outbound: {err}")
        return []