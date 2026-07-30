import spredSheet
import outbound
from dotenv import load_dotenv
import os
from gspread_formatting import CellFormat, Color, format_cell_range
load_dotenv()

verde = CellFormat(
    backgroundColor=Color(0.0, 0.8, 0.0)  # Verde
)

vermelho = CellFormat(
    backgroundColor=Color(1.0, 0.0, 0.0)  # Vermelho
)

# Conecta na planilha
spredSheetBaseBi = spredSheet.loadSpredSheet(os.getenv("SPREDSHEET_DEV"))
# Seleciona a aba pelo nome
sheet = spredSheetBaseBi.worksheet(os.getenv("SHEET_NAME_BASE_BI"))

def save(spredSheetStruct):
    
    # Verica se o registro já existe
    datas = sheet.get_all_values()

    # Mantém apenas as linhas que possuem pelo menos uma célula preenchida
    datas = [linha for linha in datas if any(celula.strip() for celula in linha)]
    
    # Verifica se registro ja exist
    exists = any(
        len(linha) > 1 and
        linha[0].strip().upper() == spredSheetStruct[0].strip().upper()
        for linha in datas[1:]
    )
    
    if (exists):
        print(f"já {spredSheetStruct[0]} JA EXISTE INSERIDO.")
        updateDatas(spredSheetStruct[0], spredSheetStruct[2])
    else:
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
        print(f"Devolução rastreio {spredSheetStruct[0]} Incluida com sucesso!!")

def updateDatas(trackingCode, clienteName):
    datasDevolution = outbound.loadSpredSheetOutbound(os.getenv("SPREDSHEET_DEV"),trackingCode,clienteName)
    print('#### DADOS DE DEVOLUÇÃO ####')
    print(datasDevolution)

    # Verifica se encontrou os dados
    if not datasDevolution or len(datasDevolution) < 4:
        print(f"Não foi encontrada devolução para o código {trackingCode}.")
        return
    
    nfd = datasDevolution[0]
    dataNfd = datasDevolution[1]
    usuario = datasDevolution[2]
    status = datasDevolution[3]

    try:
        cell = sheet.find(trackingCode)

        print(f"Código {trackingCode} encontrado, cliente {clienteName}")

        # Atualiza as colunas E até H da linha encontrada
        sheet.update(
            range_name=f"E{cell.row}:H{cell.row}",
            values=[
                [nfd, dataNfd, usuario, status]
            ]
        )

        if status == "Pendente":
            format_cell_range(sheet, f"H{cell.row}", vermelho)
        else:
            format_cell_range(sheet, f"H{cell.row}", verde)

        print("Planilha atualizada com sucesso!")

    except Exception as e:
        print(f"Código {trackingCode} não encontrado na planilha.")