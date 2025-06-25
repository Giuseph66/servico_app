import requests
header = { 'nome': 'jovem'}
response = requests.get("http://127.0.0.1:6532/usuarios", headers=header)
print(response.json())