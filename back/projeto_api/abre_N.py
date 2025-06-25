from pyngrok import ngrok, conf
import requests
import json
import os
import threading
import configparser  # Import para ler o arquivo de configuração
import time

# Carregar configurações do arquivo projeto_api/config.txt
config = configparser.ConfigParser()
config.read("projeto_api/config.txt")

# Ensure the [ngrok] section exists in the config
if not config.has_section("ngrok"):
    config.add_section("ngrok")
    with open("projeto_api/config.txt", "w", encoding="utf-8") as configfile:
        config.write(configfile)

ngrok_token_file = config.get("ngrok", "token_file", fallback="ngrok_token.json")
ngrok_port = config.getint("ngrok", "port", fallback=6532)
url_server_fixo = config.get("ngrok", "url_server_fixo", fallback="http://127.0.0.1:3000")

conf.get_default().ngrok_path = "C:\\ngrok\\ngrok.exe"

class ngrok_config:
    def __init__(self):
        self.port = ngrok_port
        self.token_file = ngrok_token_file

    def load_token(self):
        """Load the token from the JSON file."""
        if os.path.exists(self.token_file):
            with open(self.token_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("token")
        else:
            with open(self.token_file, "w", encoding="utf-8") as file:
                json.dump({"token": ''}, file, ensure_ascii=False, indent=4)
                return None
        return None

    def save_token(self, token):
        """Save the token to the JSON file."""
        with open(self.token_file, "w", encoding="utf-8") as file:
            json.dump({"token": token}, file, ensure_ascii=False, indent=4)

    def save_public_url(self, public_url):
        """Save the public URL to the config file."""
        try:
            config.set("ngrok", "public_url", public_url)
            with open("projeto_api/config.txt", "w", encoding="utf-8") as configfile:
                config.write(configfile)
            print(f"Public URL saved successfully: {public_url}")
        except Exception as e:
            print(f"Error saving public URL: {e}")

    def testa_token(self):
        print("Testando token...")
        token = self.load_token()
        if token:
            try:
                print(f"Testing token: {token}")
                ngrok.set_auth_token(token)
                print("Token set successfully.")
            except Exception as e:
                print("Por algum motivo deu errado aqui.\n\n")
                print(f"Error setting token: {e}")
            try:
                public_url = ngrok.connect(self.port).public_url
                print(f"Testing public URL: {public_url}")
                response = requests.get(f"{public_url}/docs")
                print(f"Segundo em status code: {response.status_code}")
                if response.status_code == 200:
                    self.save_public_url(public_url)  # Salvar a public_url no config
                    return public_url
                else:
                    print(f"Public URL returned unexpected status: {response.status_code}")
            except Exception as e:
                if "ERR_NGROK_108" in str(e):
                    print("Ngrok session limit reached. Reusing the existing session.")
                print(f"Error testing public URL: {e}")

        # If the token is invalid or the URL test fails, request a new token
        try:
            print("Requesting a new token...")
            response = requests.post(f'{url_server_fixo}/check_token', json={"user": "66999086599"})  # Usar URL do config
            response_data = response.json()
            new_token = response_data.get("message")
            print(f"Token recebido: {new_token}")
            if not new_token:
                raise Exception("Failed to retrieve a new token.")
            self.save_token(new_token)
            public_url = self.testa_token()
            return public_url
        except Exception as e:
            raise Exception(f"Error requesting a new token: {e}")

    def keep_url_active(self):
        public_url = ''
        while True:
            if public_url == '':
                print("Verificando se o servidor local está ativo...")
                try:
                    public_url = self.testa_token()
                    if public_url:
                        print(f"Public URL is active: {public_url}")
                        # Enviar token e public_url para o servidor fixo
                        token = self.load_token()
                        try:
                            response = requests.post(f"{public_url}/send_url", json={
                                "token": token,
                                "public_url": public_url
                            })
                            if response.status_code == 200:
                                print("URL and token sent successfully to the fixed server.")
                                continue
                            else:
                                print(f"Failed to send URL and token. Status code: {response.status_code}")
                                print(f"Response: {response.text}")
                                continue
                        except Exception as e:
                            print(f"Error sending URL and token: {e}")
                            continue
                    else:
                        print("Public URL is not active. Reconnecting...")
                        continue
                except Exception as e:
                    print(f"Error while keeping URL active: {e}")
                    continue
            else:
                resultado = requests.get(f"{public_url}/docs")
                if resultado.status_code != 200:
                    testa_local= requests.get("http://localhost:6532/docs")
                    if testa_local.status_code == 200:
                        print("Local server is running, but public URL is not active.")
                        public_url = ''
                        continue
                    else:
                        print('Servidor fechado ou não está rodando.')
                        break
            time.sleep(60)  # Check every 60 seconds

class LocalhostVerifier:
    def __init__(self, port=ngrok_port):
        self.port = port
        self.base_url = f"http://127.0.0.1:{self.port}"

    def verify_server(self, retries=10, delay=1):
        """Verify if the FastAPI server is running on localhost."""
        print(f"Checking if FastAPI server is running on {self.base_url}...")
        for attempt in range(retries):
            try:
                response = requests.get(f"{self.base_url}/docs")
                if response.status_code == 200:
                    print(f"FastAPI server is running on {self.base_url}.")
                    return True
            except requests.ConnectionError:
                print(f"Attempt {attempt + 1}/{retries}: Server not available. Retrying in {delay} second(s)...")
                time.sleep(delay)
        print("FastAPI server did not start within the expected time.")
        return False

if __name__ == "__main__":
    verifier = LocalhostVerifier(port=ngrok_port)

    def ate_conseguir():
        if verifier.verify_server():
            ngrok_instance = ngrok_config()
            ngrok_instance.keep_url_active()
            ate_conseguir()
        else:
            ate_conseguir()
            print("Localhost server is not running. Please start the server and try again.")

    ate_conseguir()