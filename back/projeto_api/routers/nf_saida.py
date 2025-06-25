from fastapi import APIRouter, Header, HTTPException, Query
import json
import os
from typing import Optional
from ..db import get_connection
from enum import Enum

router = APIRouter()

def is_authorized(nome):
    file_path = "autorizador.json"
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return any(entry["nome"] == nome and entry["status"] for entry in data)

class OrdemEnum(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/")
def listar_nf_saida(
    nome: str = Header(None),
    quantidade: Optional[int] = Query(None, description="Número máximo de registros a retornar"),
    nota_fiscal: Optional[str] = Query(None, description="Código/ número da NF"),
    empresa: Optional[str] = Query(None, description="Empresa"),
    ordenar_por: Optional[str] = Query(None, description="Campo pelo qual ordenar"),
    ordem: OrdemEnum = Query(OrdemEnum.asc, description="asc ou desc")
):
    if not nome or not is_authorized(nome):
        raise HTTPException(status_code=403, detail="Usuário não permitido.")

    # ---------------------------------------------
    # Monta SELECT com suporte a FIRST (Firebird)
    # ---------------------------------------------
    select_clause = "SELECT"
    if quantidade is not None and quantidade > 0:
        select_clause += f" FIRST {quantidade}"
    base_sql = f"{select_clause} * FROM NF_SAIDA"

    conditions = []
    params: list = []

    if nota_fiscal is not None:
        conditions.append("NOTA_FISCAL = ?")
        params.append(nota_fiscal)

    if empresa is not None:
        conditions.append("EMPRESA = ?")
        params.append(empresa)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    # Ordenação
    if ordenar_por:
        # Sanitiza nome de coluna permitido (evita injection)
        allowed_columns = {"NOTA_FISCAL", "DATA_EMISSAO", "QUANTIDADE", "NFS", "EMPRESA"}
        if ordenar_por.upper() not in allowed_columns:
            raise HTTPException(status_code=400, detail="Campo de ordenação inválido.")
        base_sql += f" ORDER BY {ordenar_por} {ordem.value.upper()}"
    print(base_sql, params)
    con = get_connection()
    cur = con.cursor()
    cur.execute(base_sql, params)
    colunas = [desc[0] for desc in cur.description]
    dados = [dict(zip(colunas, row)) for row in cur.fetchall()]
    con.close()
    return dados
