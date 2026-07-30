import os
import gspread 
from google.oauth2.service_account import Credentials
from datetime import datetime
import dataBase
import unicodedata

SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive"
    ]

# pagina13, grupo oscar, base_nfd
EXCLUSE_SHEETS = [785626510, 2000806052,1104155334]
# QA
# SPREDSHEET_REC = "1MjIf9kiIRCurBzgJQo4AiO8BNBIq84rnQV_OY3Uh7Po"
#  QA
# SPREDSHEET_DEV = "1Byxm7-7aBR8Qevyt79N2YmlpsxDNJmoKHZFDmMC73VQ"
SPREDSHEET_REC = "1o6Fwg6Ts2DmHE7LueILg-A7wzPRt2SIQt2_fp5Q4VCE"
SPREDSHEET_DEV = "19vwitPIc9LQ1KRvGDKN9CZx1hFHfQVGAPyI2gMjjzSw"
SPREDSHEETS = [SPREDSHEET_REC,SPREDSHEET_DEV]
NAMETABLES = ['tb_inbound', 'tb_devolution']

list_datas_inbound: list = []
list_datas_dev: list = []

# ACESSO AS PLANILHAS DO GOOGLE
def loadSpredSheet(spredSheet_Id):
    print("Carregando dados")
    credenciais = Credentials.from_service_account_file(
        "project-reversa-e1e51cb24f7b.json",
        scopes=SCOPES
    )
    
    client = gspread.authorize(credenciais)

    # spredSheet = cliente.open(sheet_name)
    spredSheet = client.open_by_key(spredSheet_Id)

    return spredSheet

# LE A PLANILHA DE RECEBIMENTO
def loadDatasRec(sheet_id):
    print(f'########## DOWNLOAD SHEET RECEBIMENTO ############')
    spredSheet = loadSpredSheet(sheet_id)
    tableName = formatTitle(spredSheet)
    sheet1 = spredSheet.sheet1
    datas_sheet1 = sheet1.get_all_values()

    cont = 0
    
    for data in datas_sheet1[:]:
        try:
            
            data_entrada_value = datetime.strptime(data[3],"%d/%m/%Y").date()
            if(data_entrada_value.year >= 2026):
                dados = dataBase.selectAll('pedido_chave',tableName )

                if data[1] in dados:
                    print(f"{data[1]} já existe no banco")
                else:
                    dataBase.insertDatasInbound(data,tableName)
                
                # if cont > 100:
                #     break
                # cont = cont + 1
            
        except ValueError:
            print(f"Valor {data[3]} não valido para data!!!")
    
    dataBase.closeConnection()

# LE A PLANILHA DE DEVOLUÇÃO
def loadDatasDev(sheet_id):
    print(f'########## DOWNLOAD SHEET DEVOLUÇÃO ############')
    
    # Carrega a planilha
    spredSheet = loadSpredSheet(sheet_id)

    tableName = formatTitle(spredSheet)

    # Obtem todas as abas
    sheets = spredSheet.worksheets()

    
    
    # Percorre os dados de cada aba
    for sheet in sheets:
        
        if(sheet.id in EXCLUSE_SHEETS):
            continue
        
        # Obtem os dados da aba corrente de devolução 
        datas_dev = sheet.get_all_values()
        
        # Lista de recebimentos efetuados
        for data in datas_dev:
            
            # pedido_chave_inbound: str = data[1]
            try:
                data_entrada_value = datetime.strptime(data[2],"%d/%m/%Y").date()
                
                if(data_entrada_value.year >= 2026):
                    print(data)
                    data.append(sheet.title)

                    # Verifica registros duplicados
                    dados = dataBase.selectAll('codigorastreio', tableName)
                    if data[0] in dados:
                        print(f'{data[0]} já existe!!')
                    else:
                        print(f'Inserindo {data[0]} no banco!!')
                        dataBase.insertDatasDevolution(data,tableName)
            except ValueError:
                print(f"Valor {data[2]} não valido para data!!!")
        data.clear()
            
    # print(list_datas_dev)      
    # compareDatas()  
    dataBase.closeConnection()    

# Calcula tempo de processaomento em dias
def calcProcessTime(dateStr, currentDate):
    
    try:
        oldDate = datetime.strptime(dateStr.strip(), "%d/%m/%Y").date()
        days = (currentDate - oldDate).days
        return days
    except Exception as err:
        print("Erro no input de datas",err)

def addLineInSpred(spredSheet_id, spredSheetStruct):
    # Carrega a planilha
    spredSheet = loadSpredSheet(spredSheet_id)

    # Seleciona a aba pelo nome
    sheet = spredSheet.worksheet("BASE_BI")

    # Adiciona uma linha no final
    sheet.append_row(spredSheetStruct)

def insertOrUpdateSpredBaseBi(spredSheet_id, spredSheetStruct):
    # Carrega a planilha
    spredSheet = loadSpredSheet(spredSheet_id)

    # Seleciona a aba pelo nome
    sheet = spredSheet.worksheet("BASE_BI")
    datas_sheet_base = sheet.get_all_values()

    if (len(datas_sheet_base) <= 1):
        addLineInSpred(s)

    for datasSheet in datas_sheet_base[1:]:
        print(datasSheet)
        codigoRastreio = spredSheetStruct[0]
        nfd = spredSheetStruct[4]
        status = spredSheetStruct[7]

        # se codigoRastreio existe na base,
        if  codigoRastreio == datasSheet[0].strip().upper():
            print("entrou aki")
            # verifica se tem nfd emitida
            if (nfd is not None and status != "Efetivado"):
                cell = sheet.find(codigoRastreio)
                if cell:
                    sheet.update_cell(cell.row, 8, "Efetivado")
        else:
            print("add line")
            addLineInSpred(spredSheet_id,spredSheetStruct)

    return 

def saveDatasInBaseBi():
    currentDate = currentDate = datetime.now().date()
    devolution = dataBase.findDatasDevol()

    # ESTRUTURA DA PLANILHA = rastreio|DataRecebimento|Cliente|Transportadora|NFD|DataNFD|Usuario|Status|TempoProcessamento
    for r in devolution:
        codigorastreio = r[0].strip()
        nfd = r[1].strip()
        data =r[2].strip()
        user=r[3].strip()
        status= "Efetivado" if nfd is not None else "Pendente"

        print(f'##### ANALISANDO CODIGO RASTREIO -> {codigorastreio}#######')
        
        datasReceb = dataBase.findDatasReceb(codigorastreio).split(",")
        print(datasReceb)

        if datasReceb and datasReceb != ['']:
            spredSheetStruct = [
                codigorastreio.strip().upper(), #rastreio
                datasReceb[1],  #datarecebimento
                datasReceb[2],  #cliente
                datasReceb[3],  #transportadora
                nfd,            
                data,
                user,
                status
            ]


        else:
            print("Codigo rastreio não encontrado no tabela de recebimento")
            continue

        # calcula tempo de processamento
        processTimeDays = calcProcessTime(datasReceb[1], currentDate)
        spredSheetStruct.append(processTimeDays)

        isCodigoRastreioExist = dataBase.isExists(codigorastreio,"tb_base_bi","CODIGORASTREIO")

        if isCodigoRastreioExist:
            if (nfd and status != "Efetivado"):
                status = "Efetivado"
                dataBase.updateBaseBi(status,nfd,data,user,codigorastreio)
        else:
            # insere os dados consolidados na tabela tb_base_bi
            dataBase.insertIntoBaseBi(spredSheetStruct)

def getHeaders(sheet_id):
    spredSheet = loadSpredSheet(sheet_id)
    sheet1 = spredSheet.sheet1
    header = sheet1.get_all_values()[0]
    return header,spredSheet

def menu():
    while True:
        os.system("cls")  # Windows

        print("=" * 40)
        print(" Menu de cofiguração")
        print("=" * 40)
        print("1 - Create Tables")
        print("2 - Carrega planilha de recebimento")
        print("3 - Carrega planilha de devolução ")
        print("4 - Gravar dados na BASE_BI")
        print("5 - Consolidar dados ")
        print("0 - Sair")
        print("=" * 40)

        option = input("Choose option: ")

        if option == "1":
            print('opção 1')
            createTables()
            break
        if option == "2":
            print('opção 1')
            loadDatasRec(SPREDSHEET_REC)
            break
        elif option == "3":
            print('opção 3')
            loadDatasDev(SPREDSHEET_DEV)
            break
        elif option == "4":
            print('opção 4')
            saveDatasInBaseBi()
            break
        elif option == "5":
                print('opção 5')
                break
        elif option == "0":
            print("Encerrando...")
            break

        else:
            print("\nOpção inválida!")
            input("Pressione ENTER para continuar...")
    

if __name__ == '__main__':
    menu()
