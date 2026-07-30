import sqlite3
import re
import unicodedata

PREFIXTB = "tb"
fieldTextFormated = []

conn = sqlite3.connect("db_inboundDevol.db")
cursor = conn.cursor()

def normalize(fieldText):

    for f in fieldText:
        print(f)
        f = unicodedata.normalize('NFKD', f).encode('ASCII', 'ignore').decode('ASCII')
        f = f.upper()
        f = f.replace(" ", "").replace("/","_")
        f = f.replace(".", "")
        
        fieldTextFormated.append(f)
    
def createTables(tableName, tableFields:list, fieldAux:str = None):
    normalize(tableFields)
    print(fieldTextFormated)

    if fieldAux is None:
        fields_sql = (
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "  + ", ".join(f"{field} TEXT" for field in fieldTextFormated)
        )
    else:
        fieldTextFormated.append(fieldAux)
        fields_sql = (
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "  + ", ".join(f"{field} TEXT" for field in fieldTextFormated)
        )
    
    # print(fields_sql)
    
    sql = f" CREATE TABLE IF NOT EXISTS {tableName}({fields_sql}) "

    print(sql)
    cursor.execute(sql)
    conn.commit()
    fieldTextFormated.clear()

def createTableBaseBi():
    sql = """
            CREATE TABLE "tb_base_bi" (
                "id"	INTEGER,
                "codigorastreio"	TEXT,
                "datarecebimento"	TEXT,
                "cliente"	TEXT,
                "transportadora"	TEXT,
                "nfd"	TEXT,
                "data"	TEXT,
                "usuario"	TEXT,
                "status"	TEXT,
                "tempoProcessamento"	TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
        """

def insertIntoBaseBi(datas):
    print("### Inserindo dados na tabela inbound ######")
    print(datas)
    cursor.execute(f""" INSERT INTO tb_base_bi(
        codigorastreio,
        datarecebimento,
        cliente,
        transportadora,
        nfd,
        data,
        usuario,
        status,
        tempoProcessamento
    ) VALUES ( ?,?,?,?,?,?,?,?,?) """, datas)
    conn.commit()

def insertDatasInbound(datas, tableName):
    print("### Inserindo dados na tabela inbound ######")
    print(datas)
    cursor.execute(f""" INSERT INTO {tableName}(
        HORA,
        PEDIDO_CHAVE,
        TRANSPORTADORA,
        DATA_ENTREGA,
        MES_ENTREGA,
        USUARIO,
        TIPO_DEVOLUCAO,
        CLIENTE,
        DEVOLUCAO,
        AGENDAMENTO,
        OBSERVACOADAENTREGA,
        VOLUMES
    ) VALUES ( ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, datas)
    conn.commit()

def insertDatasDevolution(datas,tableName):
    print("### Inserindo dados na tabela devolution ######")
    print(datas)
    cursor.execute(f"""
        INSERT INTO {tableName} (
            codigorastreio,
            nfd,
            data ,
            user ,
            obs ,
            status , 
            cliente
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, datas)

    conn.commit()

def selectAll(fieldKey, tableName):
    cursor.execute(f"SELECT {fieldKey} FROM {tableName}")
    lista = [linha[0] for linha in cursor.fetchall()]
    return lista

def isExists(pedido_chave: str, tableName: str, fieldKey:str):
    pedido_chave = pedido_chave.strip()
    cursor.execute(f"SELECT {fieldKey} FROM {tableName} WHERE CODIGORASTREIO = ?",(pedido_chave,))
    result = cursor.fetchone()
    if result:
        return True
    return False

def updateBaseBi(status,nfd,data,usuario,codigorastreio):
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tb_base_bi
        SET STATUS = ?, NFD=?, DATA=?, USUARIO=?
        WHERE codigorastreio = ?
    """, (status,nfd,data,usuario,codigorastreio))

    conn.commit()

def findDatasDevol():
    # cursor.execute(f"SELECT {fieldKey} FROM {tableName}")
    cursor.execute(f"SELECT CODIGORASTREIO,NFD, DATA, USER, CLIENTE FROM tb_qa_devolucao2026")
    datas =  cursor.fetchall()
    return datas

def findDatasReceb(pedido_chave):
    cursor.execute("""
        SELECT pedido_chave, dataentrega, Cliente, Transportadora
        FROM tb_qa_recdoca_rev
        WHERE pedido_chave = ?
    """, (pedido_chave.strip(),))

    resultado = cursor.fetchone()

    if resultado:
        return ", ".join(map(str, resultado))
    return ""

def closeConnection():
        cursor.close()
        conn.close()


if __name__ == '__main__':
    createTables()