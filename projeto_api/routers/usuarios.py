from fastapi import APIRouter, Header, HTTPException
import configparser
import fdb
import platform
import fdb.fbcore as fbcore
import json
import os

def my_b2u(st, charset):
    if charset.upper() == "NONE":
        return st  
    else:
        return st.decode(charset, errors="replace")

fbcore.b2u = my_b2u

print("Python Architecture:", platform.architecture())

fdb.load_api(r"C:\Program Files (x86)\Firebird\Firebird_5_0\fbclient.dll")

config = configparser.ConfigParser()
config.read(r"C:\Athenas Sistemas\dbxconnections.ini", encoding="utf-8-sig")
cfg = config["Athenas"]

router = APIRouter()

def get_connection():
    """Create a new database connection."""
    return fdb.connect(
        dsn=cfg["database"].strip('"'),
        user=cfg["user_name"],
        password=cfg["password"],
        charset="NONE", 
        sql_dialect=int(cfg.get("sqldialect", 3))
    )

def is_authorized(nome):
    file_path = "autorizador.json"
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return any(entry["nome"] == nome and entry["status"] for entry in data)

@router.get("/")
def listar_usuarios(nome: str = Header(None)):
    if not nome or not is_authorized(nome):
        raise HTTPException(status_code=403, detail="Usuário não permitido.")
    con = get_connection() 
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM USUARIOS")
        colunas = [desc[0] for desc in cur.description]
        dados = [dict(zip(colunas, row)) for row in cur.fetchall()]
        return dados
    finally:
        con.close()  