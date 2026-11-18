
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.milvus.com.br/api/dispositivos/grupos/dropdownlist"

resposta = requests.get(
    url,
    headers={
        "Authorization": os.getenv("MILVUS_WEB_TOKEN")
    },
    timeout=60
)

resposta.raise_for_status()

grupos = resposta.json().get("dropDown", [])

for grupo in grupos:
    nome = grupo.get("text", "")
    if any(f"#{n}" in nome for n in range(1, 6)):
        print(f"{grupo['id']} | {nome}")

for grupo in grupos:
    print(f"ID: {grupo['id']} | Nome: {grupo['text']}")

print(f"\nTotal de grupos: {len(grupos)}")
