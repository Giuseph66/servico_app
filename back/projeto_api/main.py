import sys
import os
import configparser  # Import para ler o arquivo de configuração
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from fastapi import FastAPI, HTTPException, Body
from projeto_api.routers import (
    clientes, empresa, produtos, fornecedores, nf_saida, usuarios, nfs_itens,
    contas_receber, representantes, ordem_servico_comissionado, ordens_servico,
    comissoes, operacoes_fiscais
)
import requests

# Carregar configurações do arquivo projeto_api/config.txt
config = configparser.ConfigParser()
config.read("projeto_api/config.txt")

server_host = config.get("server", "host", fallback="0.0.0.0")
server_port = config.getint("server", "port", fallback=6532)
autorizador_file_path = config.get("autorizador", "file_path", fallback="autorizador.json")

app = FastAPI()

app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(empresa.router, prefix="/empresa", tags=["Empresa"])
app.include_router(produtos.router, prefix="/produtos", tags=["Produtos"])
app.include_router(fornecedores.router, prefix="/fornecedores", tags=["Fornecedores"])
app.include_router(nf_saida.router, prefix="/nf_saida", tags=["NF Saída"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(nfs_itens.router, prefix="/nfs_itens", tags=["NFs Itens"])
app.include_router(contas_receber.router, prefix="/contas_receber", tags=["Contas a Receber"])
app.include_router(representantes.router, prefix="/representantes", tags=["Representantes"])
app.include_router(ordem_servico_comissionado.router, prefix="/ordem_servico_comissionado", tags=["Ordem Serviço Comissionado"])
app.include_router(ordens_servico.router, prefix="/ordens_servico", tags=["Ordens de Serviço"])
app.include_router(comissoes.router, prefix="/comissoes", tags=["Comissões"])
app.include_router(operacoes_fiscais.router, prefix="/operacoes_fiscais", tags=["Operações Fiscais"])


@app.post("/autorizador")
def autorizador(nome: str = Body(..., embed=True)):
    file_path = autorizador_file_path  # Usar o caminho do arquivo do projeto_api/config.txt
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = []

        for entry in data:
            if entry["nome"] == nome:
                if entry["status"]:
                    return {"message": "Registro já existente e ativo."}
                else:
                    return {"message": "Registro Aguardando autorização."}

        new_entry = {"nome": nome, "status": False}
        data.append(new_entry)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return {"message": "Registro salvo com sucesso e aguardando autorização."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o nome: {e}")

@app.post("/send_url")
def send_url(token: str = Body(...), public_url: str = Body(...)):
    """Send the token and public URL to the fixed server."""
    print(f"Token: {token}")
    print(f"Public URL: {public_url}")
    try:
        # Ensure url_server_fixo is valid
        url_server_fixo = config.get("ngrok", "url_server_fixo", fallback=None)
        if not url_server_fixo:
            raise HTTPException(status_code=500, detail="The 'url_server_fixo' is not configured in projeto_api/config.txt.")
        print(f"URL do servidor fixo: {url_server_fixo}")
        response = requests.post(f"{url_server_fixo}/urls", json={
            "token": token,
            "public_url": public_url
        })
        if response.status_code == 200:
            print("URL and token sent successfully.")
            return {"message": "URL and token sent successfully."}
        else:
            print(f"Failed to send URL and token. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send URL and token.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending URL and token: {e}")

if __name__ == "__main__":
    import uvicorn
    import subprocess

    subprocess.run(['./inicia.sh'], shell=True)

    uvicorn.run("main:app", host=server_host, port=server_port, reload=False)

