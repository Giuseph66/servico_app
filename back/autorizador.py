import requests

url = "http://localhost:8000/autorizador"
payload = { "nome": "jovem" }

response = requests.post(url, json=payload)
print(response.json())
