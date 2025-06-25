from fastapi import APIRouter, Header, HTTPException
import json
import os
from ..db import get_connection

router = APIRouter()

def decode_value(value, encoding="WIN1252"):
    if isinstance(value, bytes):
        return value.decode(encoding, errors="replace")
    return value

def is_authorized(nome):
    file_path = "autorizador.json"
    if not os.path.exists(file_path):
        return True
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    atut=any(entry["nome"] == nome and entry["status"] for entry in data)
    print(atut)
    return atut

@router.get("/")
def listar_empresa(nome: str = Header(None)):
    print(nome)
    if not nome or not is_authorized(nome):
        raise HTTPException(status_code=403, detail="Usuário não permitido.")
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM EMPRESAS")
    colunas = [desc[0] for desc in cur.description]
    dados = []
    for row in cur.fetchall():
        registro = {col: decode_value(value) for col, value in zip(colunas, row)}
        dados.append(registro)
    con.close()
    return dados
