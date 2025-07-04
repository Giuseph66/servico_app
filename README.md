# Servico App – Guia Completo

## Visão Geral

**Servico App** é uma solução _full-stack_ para gestão comercial e de serviços que combina:

1. **Backend** em Python (FastAPI) conectando-se a uma base **Firebird**
2. **Aplicativo móvel** em React Native (Expo) com banco **SQLite** offline-first
3. **Scripts utilitários** e uma interface em Tkinter para administração/diagnóstico

O propósito central é expor de forma segura dados corporativos (Clientes, Produtos, NF-e, Ordens de Serviço, etc.) através de uma API REST e permitir que agentes externos (aplicativo ou terceiros) sincronizem e manipulem estas informações mesmo sem conexão constante.

---

## Estrutura do Repositório

| Caminho | Descrição |
|---------|-----------|
| `back/` | Código-fonte do backend (FastAPI) + arquivos de banco `*.FDB` + scripts auxiliares |
| `front/` | Aplicativo React Native/Expo |
| `front/services/` | Rotinas de sincronização de dados entre API ⇄ SQLite |
| `front/config/database.ts` | Camada de acesso ao SQLite com _migrations_ |
| `back/projeto_api/tk_manager.py` | Painel gráfico para testar endpoints & gerenciar autorizações |

---

## Funcionalidades Principais

### Backend

* Endpoints agrupados em _routers_ (ex.: `/clientes`, `/produtos`, `/usuarios`, `/nf_saida`, etc.)
* Middleware de **autorização** via cabeçalho `nome` + arquivo `autorizador.json`
* Conexão otimizada ao Firebird via biblioteca `fdb`, incluindo _fallbacks_ automáticos para localização da `libfbclient`
* Script `inicia.sh` para iniciar rapidamente um contêiner Firebird já populado

### Frontend

* Implementado com **Expo Router** (React Native 0.79) – roteamento baseado em arquivos
* Banco local SQLite com _migrations_ automáticas e sincronia incremental
* Serviços de sincronização em lote (`services/sync.ts`) com controle de _locks_
* Suporte a **offline-first**: o app funciona sem Internet e reconcilia assim que online

### Ferramentas Extras

* **Endpoint Manager** (`tk_manager.py`): GUI Tkinter para  
  ‑ Listar endpoints `GET` disponíveis
  ‑ Testar requisições rapidamente
  ‑ Gerenciar autorizações em `autorizador.json`

---

## Pré-requisitos

| Tecnologia | Versão recomendada |
|------------|--------------------|
| Python | 3.10+ |
| Node.js | 20 LTS |
| Docker | 24+ (para Firebird) |
| Expo CLI | `npm i -g expo-cli` |

> Obs.: No Linux é necessário ter as dependências de compilação do `fdb` e a _client library_ do Firebird.

---

## Configuração do Backend

1. Acesse a pasta do backend:
   ```bash
   cd back
   ```
2. (Opcional) Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv && source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt  # gere este arquivo com `pip freeze > requirements.txt` caso ainda não exista
   ```
4. Inicie o contêiner Firebird já preparado (ID de exemplo):
   ```bash
   ./inicia.sh         # apenas "docker start <ID>"
   # ou
   docker run -d --name firebird -p 3051:3051 jacobalberty/firebird:5.0
   ```
5. Execute o servidor:
   ```bash
   uvicorn projeto_api.main:app --host 0.0.0.0 --port 8000
   ```
6. Acesse a documentação automática em `http://localhost:8000/docs`

### Variáveis & Configuração

As portas, host e caminho de `autorizador.json` podem ser ajustados em `back/projeto_api/config.txt`.

---

## Configuração do Frontend

1. Entre na pasta do app:
   ```bash
   cd front
   ```
2. Instale as dependências:
   ```bash
   npm install  # ou yarn
   ```
3. Inicie o projeto:
   ```bash
   npx expo start
   ```
4. Escolha abrir no **Emulador Android**, **Simulador iOS** ou via **Expo Go**.

### Apontando para a API

O arquivo/utilitário que define a URL base da API fica em `constants` ou diretamente nos serviços.  <br>
Altere `const BASE_URL = "http://<ip_da_api>:8000"` conforme o ambiente.

---

## Sincronização de Dados

1. O app dispara rotinas do módulo `services/sync.ts` que fazem `fetch` paginado dos endpoints
2. Dados são persistidos no SQLite usando `config/database.ts`
3. As tabelas são criadas automaticamente na primeira execução (_migrations_)
4. O progresso de sincronia é logado no console Metro/Expo

> Caso deseje reiniciar completamente o local DB: `npm run reset-project` ou chame `resetDatabase()` no console.

---

## Testes Rápidos com o Endpoint Manager

```bash
python back/projeto_api/tk_manager.py
```

Permite testar `GET /<endpoint>` e alternar autorizações sem precisar de ferramentas externas.

---

## Próximos Passos / TODO

- [ ] Criar arquivo `requirements.txt` fixando versões do backend
- [ ] Adicionar **docker-compose** unificando API + Firebird
- [ ] Pipeline CI (lint + testes automatizados)

---

## Licença

Projeto privado — todos os direitos reservados.
