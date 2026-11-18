
import os
import json
import requests
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

TOKEN = os.getenv("MILVUS_WEB_TOKEN", "").strip()
URL = "https://api.milvus.com.br/api/dispositivos/grupos/dropdownlist"

if not TOKEN:
    raise ValueError("MILVUS_WEB_TOKEN não configurado no .env")


def consultar_grupos():
    # Remove o prefixo, caso já esteja presente no .env
    token = TOKEN.removeprefix("Bearer ").strip()

    print("Consultando grupos do Milvus...")
    print(f"Token carregado: {bool(token)}")
    print(f"Tamanho do token: {len(token)} caracteres")

    # Testa os dois formatos de autenticação
    formatos = {
        "Bearer": f"Bearer {token}",
        "Token direto": token
    }

    for nome, autorizacao in formatos.items():
        print(f"\nTestando autenticação: {nome}")

        resposta = requests.get(
            URL,
            headers={
                "Authorization": autorizacao,
                "Accept": "application/json"
            },
            timeout=30
        )

        print(f"Status HTTP: {resposta.status_code}")

        if resposta.status_code == 200:
            dados = resposta.json()

            print("\n===== GRUPOS DO MILVUS =====")
            print(json.dumps(
                dados,
                indent=4,
                ensure_ascii=False
            ))

            print("\nConsulta realizada com sucesso!")
            return dados

        if resposta.status_code == 401:
            print("Autenticação não autorizada.")
            continue

        print(f"Erro HTTP: {resposta.status_code}")
        resposta.raise_for_status()

    print("\nNenhum formato de autenticação foi aceito.")
    print("Verifique se o token web está válido.")


if __name__ == "__main__":
    try:
        consultar_grupos()
    except requests.RequestException as erro:
        print(f"Erro na requisição: {erro}")
    except ValueError as erro:
        print(f"Erro: {erro}")
