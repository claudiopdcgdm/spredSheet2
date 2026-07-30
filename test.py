import dataBase
from datetime import datetime

base_bi = []
def addList():
    pass
def teste():
    currentDate = datetime.now().strftime("%d/%m/%Y")
    result = dataBase.findDatasDevol()
    for r in result:
        # print(r[0])
        codigorastreio = r[0]
        nfd = r[1]
        data =r[2]
        user=r[3]
        status=r[4]


        codigo = 'AP153365076BR'
        datasDevol = dataBase.findDatasReceb(codigo)
        print(result)
        base_bi.append((codigorastreio, datasDevol[0],datasDevol[1],datasDevol[2],nfd,data,user,status))
        
    print(base_bi)

if __name__ == '__main__':
    teste()
