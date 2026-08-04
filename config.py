from dotenv import load_dotenv, set_key
import os

ENV_FILE = ".env"

def configuration():

    load_dotenv(ENV_FILE, override=True)

    spreedSheetRecDefault = os.getenv("SPREDSHEET_REC", "")
    spreedSheetDevDefault = os.getenv("SPREDSHEET_DEV", "")
    sheetNameBaseBiDefault = os.getenv("SHEET_NAME_BASE_BI", "")
    jobRecebTimeDefault = os.getenv("TIME_UPDATE_JOB_RECEB", "5")
    jobUpdateTimeDefault = os.getenv("TIME_UPDATE_JOB_BASE", "20")
    daysLimitDevDefault = os.getenv("DAYS_LIMIT_DEV", "7")
    daysLimitRecebDefault = os.getenv("DAYS_LIMIT_RECEB", "1")

    print("\n========== CONFIGURAÇÃO ==========\n")

    spreedSheetRecebimento = input(
        f"Id Planilha de Recebimento [{spreedSheetRecDefault}]: "
    ).strip() or spreedSheetRecDefault

    spreedSheetDevolucao = input(
        f"Id Planilha de Devolução [{spreedSheetDevDefault}]: "
    ).strip() or spreedSheetDevDefault

    sheetNameBaseBi = input(
        f"Nome da guia Base BI [{sheetNameBaseBiDefault}]: "
    ).strip() or sheetNameBaseBiDefault

    jobTimeReceb = input(
        f"Tempo sincronização Recebimento (horas) [{jobRecebTimeDefault}]: "
    ).strip() or jobRecebTimeDefault

    jobTimeUpdate = input(
        f"Tempo sincronização Base BI (min) [{jobUpdateTimeDefault}]: "
    ).strip() or jobUpdateTimeDefault

    daysLimitDev = input(
        f"Dias limite Devolução [{daysLimitDevDefault}]: "
    ).strip() or daysLimitDevDefault

    daysLimitReceb = input(
        f"Dias limite Recebimento [{daysLimitRecebDefault}]: "
    ).strip() or daysLimitRecebDefault

    # Salva no .env
    set_key(ENV_FILE, "SPREDSHEET_REC", spreedSheetRecebimento)
    set_key(ENV_FILE, "SPREDSHEET_DEV", spreedSheetDevolucao)
    set_key(ENV_FILE, "SHEET_NAME_BASE_BI", sheetNameBaseBi)
    set_key(ENV_FILE, "TIME_UPDATE_JOB_RECEB", jobTimeReceb)
    set_key(ENV_FILE, "TIME_UPDATE_JOB_BASE", jobTimeUpdate)
    set_key(ENV_FILE, "DAYS_LIMIT_DEV", daysLimitDev)
    set_key(ENV_FILE, "DAYS_LIMIT_RECEB", daysLimitReceb)

    # Recarrega as variáveis do .env
    load_dotenv(ENV_FILE, override=True)

    print("\n===================================")
    print("Configurações salvas com sucesso!")
    print("===================================\n")
    input("Pressione ENTER para continuar...")