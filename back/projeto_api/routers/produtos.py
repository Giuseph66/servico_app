from fastapi import APIRouter, Header, HTTPException
import json
import os
from ..db import get_connection
from starlette.concurrency import run_in_threadpool

router = APIRouter()

def decode_value(value, encoding="windows-1252"):
    if isinstance(value, bytes):
        return value.decode(encoding, errors="replace")
    return value

def listar_produtos_sync():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM PRODUTOS")
    colunas = [desc[0] for desc in cur.description]
    dados = []
    for row in cur.fetchall():
        registro = {col: decode_value(value) for col, value in zip(colunas, row)}
        dados.append(registro)
    con.close()
    return dados

def is_authorized(nome):
    file_path = "autorizador.json"
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return any(entry["nome"] == nome and entry["status"] for entry in data)

@router.get("/")
async def listar_produtos(nome: str = Header(None)):
    if not nome or not is_authorized(nome):
        raise HTTPException(status_code=403, detail="Usuário não permitido.")
    return await run_in_threadpool(listar_produtos_sync)
