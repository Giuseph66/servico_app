import requests
import json
import time

# Verificar se o servidor está ativo
def check_server_status():
    try:
        response = requests.get('http://localhost:8000/docs')
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Erro ao verificar o status do servidor: {e}")
        return False

# Obter todos os caminhos disponíveis da API com método GET
def get_api_get_paths():
    try:
        response = requests.get('http://localhost:8000/openapi.json')
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            get_paths = [path for path, methods in paths.items() if "get" in methods]
            return get_paths
        else:
            print(f"Erro ao obter os caminhos da API. Código de status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro ao obter os caminhos da API: {e}")
        return []

# Exportar os caminhos GET para um arquivo JSON
def export_paths_to_file(paths, filename="api_get_paths.json"):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(paths, file, ensure_ascii=False, indent=4)
        print(f"Caminhos GET exportados com sucesso para {filename}")
    except Exception as e:
        print(f"Erro ao exportar os caminhos para o arquivo: {e}")

if __name__ == "__main__":
    ini_time = time.time()
    if check_server_status():
        print("Servidor está ativo.")
        paths = get_api_get_paths()
        if paths:
            print(f"Total de caminhos GET encontrados: {len(paths)}")
            print("Caminhos GET encontrados:")
            for path in paths:
                print(path)
            export_paths_to_file(paths)
        else:
            print("Nenhum caminho GET encontrado.")
    else:
        print("Servidor não está ativo.")
    print("Tempo de execução:", time.time() - ini_time)