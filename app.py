import os
from dotenv import load_dotenv
from datetime import datetime
import inbound
import outbound

load_dotenv()
  
def menu():
    while True:
        os.system("cls")  # Windows

        print("=" * 40)
        print(" Menu de cofiguração")
        print("=" * 40)
        print("1 - Carrega planilha de recebimento")
        print("2 - Carrega planilha de devolucao")
        # print("3 - Carrega planilha de devolução ")
        # print("4 - Gravar dados na BASE_BI")
        # print("5 - Consolidar dados ")
        print("0 - Sair")
        print("=" * 40)

        option = input("Choose option: ")

        if option == "1":
            print('Load SpredSheet Inbound')
            inbound.loadSpredSheetInbound(os.getenv("SPREDSHEET_REC"))
            break
        if option == "2":
            print('Load SpeedSheet Outbound')
            outbound.loadSpredSheetOutbound(os.getenv("SPREDSHEET_DEV"))
            break
        elif option == "3":
            print('opção 3')
            break
        elif option == "4":
            print('opção 4')
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
