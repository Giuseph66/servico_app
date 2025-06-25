# -*- coding: utf-8 -*-

"""Módulo utilitário para conexão Firebird.

Fornece ``get_connection`` que faz a carga inteligente da biblioteca
``libfbclient`` antes de abrir a conexão. O caminho é resolvido a partir
da variável de ambiente ``FIREBIRD_LIB`` ou de alguns locais comuns.
"""

from __future__ import annotations

import fdb
import platform
import os
import configparser


def load_firebird_api() -> None:
    """Carrega a biblioteca cliente do Firebird se ainda não estiver carregada.

    A estratégia é:
    1. Se a variável de ambiente ``FIREBIRD_LIB`` estiver definida e o
       arquivo existir, usa-se esse caminho.
    2. Caso contrário, percorre uma lista de caminhos comuns para encontrar
       o ``libfbclient.so``.
    3. Por fim, tenta chamar ``fdb.load_api()`` sem parâmetros para deixar
       o *driver* procurar sozinho. Se nada funcionar, levanta uma exceção
       com instruções de instalação.
    """

    # Evita recarregar se já foi feito em outro módulo.
    if getattr(fdb, "api", None):
        return

    candidate_paths = []

    # 1. Valor fornecido pelo usuário
    env_path = os.getenv("FIREBIRD_LIB")
    if env_path:
        candidate_paths.append(env_path)

    # 2. Alguns locais comuns (podem ser expandidos se necessário)
    candidate_paths.extend([
        "/opt/firebird/lib/libfbclient.so.5.0.2",  # Versão específica do Docker
        "/opt/firebird/lib/libfbclient.so.5",
        "/usr/lib/x86_64-linux-gnu/libfbclient.so.5",
        "/usr/lib64/libfbclient.so.3",
        "/usr/lib/libfbclient.so",
    ])

    for path in candidate_paths:
        if path and os.path.exists(path):
            try:
                fdb.load_api(path)
                return
            except Exception:
                # continua tentando os próximos
                pass

    # 3. Deixa o fdb procurar no *LD_LIBRARY_PATH* / default
    try:
        fdb.load_api()
        return
    except Exception:
        raise RuntimeError(
            "Não foi possível localizar a biblioteca cliente do Firebird. "
            "Defina a variável de ambiente FIREBIRD_LIB ou instale o "
            "pacote libfbclient apropriado para o seu sistema."
        )


def get_connection():
    print("Python Architecture:", platform.architecture())

    # Garante que a biblioteca cliente do Firebird esteja carregada.
    load_firebird_api()

    # Conecta exatamente como no test_docker_approach.py
    return fdb.connect(
        dsn='127.0.0.1/3051:/firebird/data/ATHENAS.FDB',
        user='SYSDBA',
        password='masterkey',
        fb_library_name='/opt/firebird/lib/libfbclient.so.5.0.2',
        charset='WIN1252',
    )
