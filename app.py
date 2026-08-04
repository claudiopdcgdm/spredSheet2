import os
from dotenv import load_dotenv
import inbound
import outbound
import scheduller

load_dotenv()
  
def menu():
    while True:
        os.system("cls")  # Windows
        print("Developer By CPM")
        print("=" * 40)
        print(" Menu de cofiguração")
        print("=" * 40)
        print("1 - Start Automation")
        print("2 - Load SpredSheet Inbound (Recebimento)")
        print("3 - Update SpredSheet Base_Bi_2 ")
        print("4 - Configurations")
        print("0 - Exit")
        print("=" * 40)

        option = input("Choose option: ")

        if option == "1":
            print("Iniciando automação")
            scheduller.start()
            break
        if option == "2":
            print('Carregar planilha recebimento')
            inbound.run(os.getenv("SPREDSHEET_REC"))
            break
        elif option == "3":
            print('Atualizar Base')
            outbound.run()
            break
        elif option == "4":
            print('Configurações')
            break
        elif option == "0":
            print("Encerrando...")
            break

        else:
            print("\nOpção inválida!")
            input("Pressione ENTER para continuar...")
    

if __name__ == '__main__':
    menu()
