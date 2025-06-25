from fastapi import APIRouter, Header, HTTPException
import json
import os
from ..db import get_connection

router = APIRouter()

def is_authorized(nome):
    file_path = "autorizador.json"
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return any(entry["nome"] == nome and entry["status"] for entry in data)

@router.get("/")
def listar_comissoes(nome: str = Header(None)):
    if not nome or not is_authorized(nome):
        raise HTTPException(status_code=403, detail="Usuário não permitido.")
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM COMISSOES")
        colunas = [desc[0] for desc in cur.description]
        dados = [dict(zip(colunas, row)) for row in cur.fetchall()]
        return dados
    finally:
        con.close()
