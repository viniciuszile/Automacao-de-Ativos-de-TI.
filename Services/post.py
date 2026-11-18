
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from Config.conexao import conectar
from Config.dicionario import EMPRESAS, STATUS, INTERNO, PATRIMONIOS
from Config.log import registrar_atualizacao

BASE_URL = "https://apiintegracao.milvus.com.br/api"
DATA = Path(__file__).resolve().parent.parent / "Data"
CLIENTE_ID = 438713

SIMULAR = True
EMPRESAS_SELECIONADAS = None
LIMITE = None


def normalizar(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    return " ".join(
        "".join(c for c in texto if not unicodedata.combining(c))
        .upper().split()
    )


def identificar_destino(dispositivo):
    apelido = str(dispositivo.get("apelido") or "").strip()
    patrimonio = normalizar(dispositivo.get("patrimonio"))

    status = re.match(r"^(#[1-5])(?=\s|$)", apelido)

    if status and status.group(1) in STATUS:
        sigla, nome, grupo_id = STATUS[status.group(1)]
        return sigla, {"grupo": nome, "grupo_id": grupo_id}

    partes = re.split(r"\s*-\s*", apelido, maxsplit=2)

    if len(partes) >= 3:
        sigla = normalizar(partes[1])
        if sigla in EMPRESAS:
            return sigla, EMPRESAS[sigla]

    if patrimonio == "INTERNO":
        return "INTERNO", INTERNO

    sigla = PATRIMONIOS.get(patrimonio)
    return (sigla, EMPRESAS[sigla]) if sigla in EMPRESAS else (None, None)


def buscar_dispositivo(api, dispositivo_id):
    resposta = api.get(
        f"{BASE_URL}/dispositivos/buscar",
        params={"id": dispositivo_id},
        timeout=30
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
        raise ValueError("Equipamento pertence a outro cliente")

    return dispositivo


def salvar_pendencias(inventario):
    pendencias = [
        {
            "id": d["id"],
            "hostname": d.get("hostname"),
            "apelido": d.get("apelido"),
            "grupo_dispositivo_id": d.get("grupo_dispositivo_id"),
            "grupo": d.get("grupo")
        }
        for d in inventario
        if normalizar(d.get("nome_fantasia")) == "RUNTALENT TECNOLOGIA"
        and not d.get("grupo")
    ]

    arquivo = DATA / "nao_identificados.json"
    temporario = arquivo.with_suffix(".tmp")

    temporario.write_text(
        json.dumps({
            "data_geracao": datetime.now().isoformat(timespec="seconds"),
            "total": len(pendencias),
            "equipamentos": pendencias
        }, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    temporario.replace(arquivo)
    return pendencias


def main():
    DATA.mkdir(parents=True, exist_ok=True)

    inventario = json.loads(
        (DATA / "dados.json").read_text(encoding="utf-8")
    )

    if not isinstance(inventario, list) or not inventario:
        raise ValueError("Inventário vazio ou inválido")

    if not SIMULAR:
        if input("Digite CONFIRMAR para executar o PUT: ").strip() != "CONFIRMAR":
            print("Operação cancelada.")
            return

    api = conectar()
    pendencias = salvar_pendencias(inventario)
    protegidos = {str(d["id"]) for d in pendencias}

    corretos = 0
    alteracoes = []
    sem_regra = []
    falhas = []

    selecionadas = (
        {normalizar(s) for s in EMPRESAS_SELECIONADAS}
        if EMPRESAS_SELECIONADAS is not None else None
    )

    processados = set()
    analisados = 0

    for local in inventario:
        dispositivo_id = local.get("id")

        if not dispositivo_id or str(dispositivo_id) in processados:
            continue

        if normalizar(local.get("nome_fantasia")) != "RUNTALENT TECNOLOGIA":
            continue

        processados.add(str(dispositivo_id))

        if str(dispositivo_id) in protegidos:
            continue

        sigla, _ = identificar_destino(local)

        if selecionadas is not None and normalizar(sigla) not in selecionadas:
            continue

        if LIMITE is not None and analisados >= LIMITE:
            break

        analisados += 1

        try:
            atual = buscar_dispositivo(api, dispositivo_id)

            if str(atual.get("grupo_dispositivo_id")) != str(
                local.get("grupo_dispositivo_id")
            ):
                falhas.append(
                    f"{local.get('hostname')}: grupo alterado desde o GET"
                )
                continue

            sigla, empresa = identificar_destino(atual)

            if empresa is None:
                sem_regra.append(local.get("hostname"))
                continue

            destino = empresa["grupo_id"]
            anterior = atual.get("grupo_dispositivo_id")

            if str(anterior) == str(destino):
                corretos += 1
                continue

            alteracoes.append({
                "hostname": local.get("hostname"),
                "atual": local.get("grupo"),
                "destino": empresa["grupo"],
                "status": "PENDENTE" if SIMULAR else "ATUALIZADO"
            })

            if SIMULAR:
                continue

            atual["grupo_dispositivo_id"] = destino

            resposta = api.put(
                f"{BASE_URL}/dispositivos/",
                json=atual,
                timeout=30
            )
            resposta.raise_for_status()

            registrar_atualizacao(
                sigla, empresa, atual, anterior, origem="PUT"
            )

        except Exception as erro:
            falhas.append(f"{local.get('hostname')}: {erro}")

    print("\n===== RESULTADO PUT =====")
    print(f"Modo: {'SIMULAÇÃO' if SIMULAR else 'REAL'}")
    print(f"Equipamentos corretos: {corretos}")
    print(f"Precisam de alteração: {len(alteracoes)}")
    print(f"Sem regra definida: {len(sem_regra)}")
    print(f"Grupos não identificados: {len(pendencias)}")
    print(f"Falhas: {len(falhas)}")

    if alteracoes:
        print("\n--- ALTERAÇÕES ---")
        for item in alteracoes:
            print(
                f"{item['hostname']}: "
                f"{item['atual']} -> {item['destino']} "
                f"[{item['status']}]"
            )

    if sem_regra:
        print("\n--- SEM REGRA ---")
        print(", ".join(sem_regra))

    if falhas:
        print("\n--- FALHAS ---")
        for erro in falhas:
            print(erro)


if __name__ == "__main__":
    main()
