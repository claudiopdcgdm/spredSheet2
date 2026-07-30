import spredSheet
import baseBi
import os
from datetime import datetime, timedelta

# Calcula tempo de processaomento em dias
def calcProcessTime(dateStr, currentDate):
    try:
        # dateIn = datetime.strptime(dateStr,"%d/%m/%Y %H:%M:%S").date()
        dateIn = dateStr
        days = (currentDate - dateIn).days
        return days
    except Exception as err:
        print("Erro no input de datas",err)

def convertDate(dataHoraRecebe):
    try:
        dateInValue = datetime.strptime(dataHoraRecebe.strip(),"%d/%m/%Y %H:%M:%S").date()
        periodDay = int(os.getenv("TIME_UPDATE", "7"))
        limitDate = datetime.now().date() - timedelta(days=periodDay)
        return dateInValue, limitDate
    except Exception as err:
        print(f"Campo {dataHoraRecebe} não poder ser convertido, {err}")

def loadSpredSheetInbound(spredSheetId):
    print(f'########## LOAD SHEET RECEBIMENTO ############')
    currentDate = currentDate = datetime.now().date()
    spredSheetLoad = spredSheet.loadSpredSheet(spredSheetId)
    sheet1 = spredSheetLoad.sheet1
    datas_sheet1 = sheet1.get_all_values()
    
    for data in datas_sheet1[2:]:
        print(data)
        try:
            dateInValue,limitDate = convertDate(data[0])
            if(dateInValue >= limitDate):
                codigoRastreio = data[1]
                transportadora = data[2]
                dataRecebimento = data[3]
                usuarioReceb = data[5]
                cliente = data[6]
                nfd = None
                dataNfd = None
                UsuarioDev = None
                status = "PENDENTE"
                tempoProcessamento = calcProcessTime(dateInValue,currentDate)

                spredSheetStruct = [
                    codigoRastreio,
                    dataRecebimento,
                    cliente,
                    transportadora,
                    nfd,
                    dataNfd,
                    UsuarioDev,
                    status,
                    tempoProcessamento,
                ]
                print(f"DADOS LISTA DE INFO: -> {spredSheetStruct}")
                baseBi.save(spredSheetStruct)
            else:
                print("Registro fora do range de data")
        except Exception as err:
            print(err)
            print(f"Erro ao ler planilha ", err)