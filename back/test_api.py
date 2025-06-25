#!/usr/bin/env python3
import requests

# Testa o endpoint de clientes
try:
    response = requests.get('http://localhost:6532/clientes/', headers={'nome': 'Admin'})
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
except Exception as e:
    print(f"Erro: {e}") 