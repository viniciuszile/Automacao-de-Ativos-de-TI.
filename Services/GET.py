
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from Config.conexao import conectar

BASE_URL = "https://apiintegracao.milvus.com.br/api"
URL_GRUPOS = "https://api.milvus.com.br/api/dispositivos/grupos/dropdownlist"

CLIENTE_ID = 438713
EMPRESA = "Runtalent Tecnologia"
TIPOS = {"notebook", "desktop", "terminal"}

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO = BASE_DIR / "Data" / "dados.json"


def consultar_grupos():
    load_dotenv(BASE_DIR / ".env", override=True)

    token = os.getenv("MILVUS_WEB_TOKEN", "").strip()
    token = token.removeprefix("Bearer ").strip()

    if not token:
        raise ValueError("MILVUS_WEB_TOKEN não configurado no .env")

    resposta = requests.get(
        URL_GRUPOS,
        headers={
            "Authorization": token,
            "Accept": "application/json"
        },
        timeout=30
    )
    resposta.raise_for_status()

    return {
        str(item["id"]): item["text"]
        for item in resposta.json()["dropDown"]
    }


def consultar_inventario(api):
    equipamentos = {}
    pagina = 1

    while True:
        resposta = api.post(
            f"{BASE_URL}/dispositivos/listagem",
            params={
                "is_paginate": "true",
                "is_descending": "true",
                "total_registros": 100,
                "pagina": pagina
            },
            json={"filtro_body": {}},
            timeout=60
        )
        resposta.raise_for_status()

        dados = resposta.json()
        lista = dados.get("lista", [])
        paginacao = dados.get("meta", {}).get("paginate", {})

        if int(paginacao.get("current_page", 0)) != pagina:
            raise ValueError(f"Paginação inválida: {pagina}")

        for item in lista:
            empresa = str(item.get("nome_fantasia") or "").strip().casefold()
            tipo = str(item.get("tipo_dispositivo_text") or "").strip().casefold()

            if empresa == EMPRESA.casefold() and tipo in TIPOS:
                equipamentos[item["id"]] = item

        if pagina >= int(paginacao["last_page"]):
            break

        pagina += 1

    return list(equipamentos.values())


def consultar_detalhes(api, dispositivo_id):
    resposta = api.get(
        f"{BASE_URL}/dispositivos/buscar",
        params={"id": dispositivo_id},
        timeout=60
    )
    resposta.raise_for_status()

    dispositivo = next(
        (
            item for item in resposta.json().get("lista", [])
            if str(item.get("id")) == str(dispositivo_id)
        ),
        None
    )

    if not dispositivo:
        raise ValueError(f"Equipamento {dispositivo_id} não encontrado")

    if str(dispositivo.get("cliente_id")) != str(CLIENTE_ID):
        raise ValueError(f"Cliente inválido no ID {dispositivo_id}")

    return dispositivo


def main():
    api = conectar()
    grupos = consultar_grupos()
    equipamentos = consultar_inventario(api)

    inventario = []

    for local in equipamentos:
        atual = consultar_detalhes(api, local["id"])
        grupo_id = atual.get("grupo_dispositivo_id")

        inventario.append({
            "id": atual["id"],
            "hostname": local.get("hostname"),
            "apelido": atual.get("apelido"),
            "nome_fantasia": EMPRESA,
            "tipo_dispositivo_text": local.get("tipo_dispositivo_text"),
            "patrimonio": atual.get("patrimonio"),
            "grupo_dispositivo_id": grupo_id,
            "grupo": grupos.get(str(grupo_id))
        })

    com_grupo = sum(
        1 for d in inventario
        if d["grupo_dispositivo_id"] is not None and d["grupo"]
    )

    sem_nome = sum(
        1 for d in inventario
        if d["grupo_dispositivo_id"] is not None and not d["grupo"]
    )

    sem_grupo = sum(
        1 for d in inventario
        if d["grupo_dispositivo_id"] is None
    )

    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    temporario = ARQUIVO.with_suffix(".tmp")

    temporario.write_text(
        json.dumps(inventario, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    temporario.replace(ARQUIVO)

    print("\n===== RESULTADO GET =====")
    print(f"Equipamentos encontrados: {len(inventario)}")
    print(f"Com grupo identificado: {com_grupo}")
    print(f"Com ID, mas sem nome: {sem_nome}")
    print(f"Sem grupo atribuído: {sem_grupo}")
    print(f"Grupos disponíveis: {len(grupos)}")
    print("Arquivo: dados.json")
    print("Status: Concluído com sucesso.")


if __name__ == "__main__":
    main()
