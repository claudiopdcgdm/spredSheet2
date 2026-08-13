import os
from dotenv import load_dotenv
import inbound
import outbound
import scheduller
import config

load_dotenv()
  
def menu():
    while True:
        os.system("cls")  # Windows
        print("Developer By CPM")
        print("=" * 40)
        print(" Automação de dados Reversa")
        print("=" * 40)
        print("1 - Iniciar Automação")
        print("2 - Executar Processo Inbound (Recebimento)")
        print("3 - Executar Processo Outbound")
        print("4 - Configurações")
        print("0 - Sair")
        print("=" * 40)

        option = input("Escolha uma opção: ")

        if option == "1":
            scheduller.start()
            break
        if option == "2":
            inbound.run(os.getenv("SPREDSHEET_REC"))
            break
        elif option == "3":
            print('Atualizar Base')
            outbound.run()
            break
        elif option == "4":
            config.configuration()
            menu()
            break
        elif option == "0":
            print("Encerrando...")
            break

        else:
            print("\nOpção inválida!")
            input("Pressione ENTER para continuar...")
    

if __name__ == '__main__':
    menu()
