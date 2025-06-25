import requests



results = requests.get("http://127.0.0.1:8000/empresa", headers={"nome": "Admin"})
print("Resultados dos testes de endpoints:" , results)
status = results.json()
print(results.status_code)
print(status)