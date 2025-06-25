from fastapi import FastAPI
import fdb
import configparser
import platform

app = FastAPI()

def get_config():
    print("Python Architecture:", platform.architecture())
    
    fdb.load_api(r"C:\Program Files (x86)\Firebird\Firebird_5_0\fbclient.dll")

    config = configparser.ConfigParser()
    config.read(r"C:\Athenas Sistemas\dbxconnections.ini", encoding="utf-8-sig")
    return config["Athenas"]

def get_connection():
    cfg = get_config()
    return fdb.connect(
        dsn=cfg["database"].strip('"'),  # tira aspas se tiver
        user=cfg["user_name"],
        password=cfg["password"],
        charset=cfg.get("servercharset", "WIN1252"),
        sql_dialect=int(cfg.get("sqldialect", 3))
    )

@app.get("/clientes")
def listar_clientes():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM CLIENTES")
    colunas = [desc[0] for desc in cur.description]
    dados = [dict(zip(colunas, row)) for row in cur.fetchall()]
    con.close()
    return dados

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("T_1:app", host="0.0.0.0", port=8000, reload=True)