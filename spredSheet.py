from dotenv import load_dotenv
import gspread 
from google.oauth2.service_account import Credentials
import os
from logger import logger
load_dotenv()


SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive"
    ]
# ACESSO AS PLANILHAS DO GOOGLE
def loadSpredSheet(spredSheet_Id):
    try:
        credenciais = Credentials.from_service_account_file(
            "project-reversa-e1e51cb24f7b.json",
            scopes=SCOPES
        )
        
        client = gspread.authorize(credenciais)

        # spredSheet = cliente.open(sheet_name)
        spredSheet = client.open_by_key(spredSheet_Id)

        return spredSheet
    except Exception as err:
        logger.info(f"Erro ao tentar conectar na planilha -> {err}")
        return None