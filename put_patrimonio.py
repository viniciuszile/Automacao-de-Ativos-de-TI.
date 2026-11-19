import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from Config.conexao import conectar

BASE_URL = "https://apiintegracao.milvus.com.br/api"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / "Data"

CLIENTE_ID = 438713

SIMULAR = False
LIMITE = None

IGNORAR_HOSTS = {
    "EMP 260",
    "E5049",
    "R0560",
    "R0510",
}

ARQUIVO_INVENTARIO = DATA / "dados.json"
ARQUIVO_EMAILS = DATA / "dados_email.json"
ARQUIVO_PENDENCIAS = DATA / "pendencias_email.json"
ARQUIVO_LOG = DATA / "logs_patrimonio.json"

PADRAO_ESPECIAL = re.compile(r"^\s*#[1-5](?=\s|$)")
PADRAO_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalizar(valor):
    return str(valor or "").strip().casefold()


def especial(apelido):
    return bool(PADRAO_ESPECIAL.match(str(apelido or "")))


def salvar_json(caminho, conteudo):
    DATA.mkdir(parents=True, exist_ok=True)

    temporario = caminho.with_suffix(".tmp")

    temporario.write_text(
        json.dumps(conteudo, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    temporario.replace(caminho)


def carregar_json(caminho):
    dados = json.loads(caminho.read_text(encoding="utf-8"))

    if not isinstance(dados, list):
        raise ValueError(f"Formato inválido: {caminho.name}")

    return dados


def indexar_emails(registros):
    indice = defaultdict(list)

    for item in registros:
        host = normalizar(item.get("host"))

        if host:
            indice[host].append(item)

    return indice


def buscar_dispositivo(api, dispositivo_id):
    resposta = api.get(
        f"{BASE_URL}/dispositivos/buscar",
        params={"id": dispositivo_id},
        timeout=30
    )

    resposta.raise_for_status()

    dispositivo = next(
        (
            item
            for item in resposta.json().get("lista", [])
            if str(item.get("id")) == str(dispositivo_id)
        ),
        None
    )

    if dispositivo is None:
        raise ValueError("Equipamento não encontrado na API")

    if str(dispositivo.get("cliente_id")) != str(CLIENTE_ID):
        raise ValueError("Equipamento pertence a outro cliente")

    return dispositivo


def registrar_log(registro):
    if ARQUIVO_LOG.exists():
        historico = json.loads(
            ARQUIVO_LOG.read_text(encoding="utf-8")
        )
    else:
        historico = []

    if not isinstance(historico, list):
        raise ValueError("Formato inválido do histórico")

    historico.append(registro)

    salvar_json(ARQUIVO_LOG, historico)


def main():
    inventario = carregar_json(ARQUIVO_INVENTARIO)
    base_emails = carregar_json(ARQUIVO_EMAILS)

    if not inventario:
        raise ValueError("Inventário vazio")

    indice_emails = indexar_emails(base_emails)

    if not SIMULAR:
        confirmacao = input(
            "\nATENÇÃO: O patrimônio será sobrescrito.\n"
            "Digite CONFIRMAR para executar o PUT: "
        ).strip()

        if confirmacao != "CONFIRMAR":
            print("Operação cancelada.")
            return

    api = conectar()

    corretos = 0
    atualizados = 0
    simulados = 0
    especiais = 0

    alteracoes = []
    pendencias = []
    falhas = []

    # Listas para conferência completa
    ja_corretos = []
    ignorados = []

    processados = set()
    analisados = 0

    for local in inventario:
        dispositivo_id = local.get("id")

        if dispositivo_id is None or str(dispositivo_id) in processados:
            continue

        if normalizar(local.get("nome_fantasia")) != "runtalent tecnologia":
            continue

        if LIMITE is not None and analisados >= LIMITE:
            break

        processados.add(str(dispositivo_id))
        analisados += 1

        host = str(local.get("hostname") or "").strip()

        # Ignorar equipamentos definidos
        if host.upper() in IGNORAR_HOSTS:
            ignorados.append(host)
            continue

        try:
            if not host:
                raise ValueError("Hostname não informado")

            atual = buscar_dispositivo(api, dispositivo_id)

            host_api = str(atual.get("hostname") or "").strip()

            if normalizar(host_api) != normalizar(host):
                raise ValueError(
                    f"Hostname divergente: {host} / {host_api}"
                )

            apelido = atual.get("apelido")
            patrimonio_anterior = atual.get("patrimonio")

            if especial(apelido):
                destino = host_api
                tipo = "ESPECIAL"
                especiais += 1

            else:
                registros = indice_emails.get(normalizar(host), [])

                if not registros:
                    pendencias.append({
                        "hostname": host,
                        "apelido": apelido,
                        "motivo": "Hostname não encontrado na base"
                    })
                    continue

                if len(registros) != 1:
                    pendencias.append({
                        "hostname": host,
                        "apelido": apelido,
                        "motivo": "Hostname duplicado na base"
                    })
                    continue

                registro = registros[0]

                email = str(registro.get("email") or "").strip()
                nome = str(registro.get("nome") or "").strip()

                if not email:
                    pendencias.append({
                        "hostname": host,
                        "nome": nome or None,
                        "motivo": "E-mail não identificado"
                    })
                    continue

                if not PADRAO_EMAIL.fullmatch(email):
                    pendencias.append({
                        "hostname": host,
                        "nome": nome or None,
                        "motivo": "E-mail inválido"
                    })
                    continue

                if not nome:
                    pendencias.append({
                        "hostname": host,
                        "motivo": "Nome do colaborador ausente"
                    })
                    continue

                destino = email
                tipo = "EMAIL"

            # Registrar equipamentos já corretos
            if normalizar(patrimonio_anterior) == normalizar(destino):
                corretos += 1

                ja_corretos.append({
                    "hostname": host,
                    "tipo": tipo,
                    "patrimonio": patrimonio_anterior
                })

                continue

            alteracao = {
                "id": dispositivo_id,
                "hostname": host,
                "tipo": tipo,
                "anterior": patrimonio_anterior,
                "destino": destino,
                "status": "SIMULADO" if SIMULAR else "PENDENTE"
            }

            alteracoes.append(alteracao)

            if SIMULAR:
                simulados += 1
                continue

            atual["patrimonio"] = destino

            resposta = api.put(
                f"{BASE_URL}/dispositivos/",
                json=atual,
                timeout=30
            )

            resposta.raise_for_status()

            verificacao = buscar_dispositivo(api, dispositivo_id)

            if normalizar(verificacao.get("patrimonio")) != normalizar(destino):
                raise ValueError(
                    "PUT enviado, mas patrimônio não confirmado"
                )

            alteracao["status"] = "ATUALIZADO"
            atualizados += 1

            registrar_log({
                "data": datetime.now().isoformat(timespec="seconds"),
                "id": dispositivo_id,
                "hostname": host,
                "tipo": tipo,
                "patrimonio_anterior": patrimonio_anterior,
                "patrimonio_novo": destino
            })

        except Exception as erro:
            falhas.append({
                "id": dispositivo_id,
                "hostname": host,
                "erro": str(erro)
            })

    salvar_json(
        ARQUIVO_PENDENCIAS,
        {
            "data_geracao": datetime.now().isoformat(timespec="seconds"),
            "total": len(pendencias),
            "equipamentos": pendencias
        }
    )

    print("\n===== RESULTADO PUT PATRIMÔNIO =====")

    print(f"Modo: {'SIMULAÇÃO' if SIMULAR else 'REAL'}")
    print(f"Equipamentos analisados: {analisados}")
    print(f"Equipamentos especiais: {especiais}")
    print(f"Patrimônios já corretos: {corretos}")
    print(f"Precisam de atualização: {len(alteracoes)}")
    print(f"Atualizações simuladas: {simulados}")
    print(f"Atualizações confirmadas: {atualizados}")
    print(f"Ignorados: {len(ignorados)}")
    print(f"Pendências: {len(pendencias)}")
    print(f"Falhas: {len(falhas)}")

    if alteracoes:
        print("\n--- ALTERAÇÕES ---")

        for item in alteracoes:
            print(
                f"{item['hostname']} [{item['tipo']}]: "
                f"{item['anterior']} -> {item['destino']} "
                f"[{item['status']}]"
            )

    if pendencias:
        print("\n--- PENDÊNCIAS ---")

        for item in pendencias:
            print(
                f"{item['hostname']}: {item['motivo']}"
            )

    if falhas:
        print("\n--- FALHAS ---")

        for item in falhas:
            print(
                f"{item['hostname']}: {item['erro']}"
            )

    # Conferência completa
    print("\n===== CONFERÊNCIA COMPLETA =====")

    print("\n--- PATRIMÔNIOS JÁ CORRETOS ---")

    for item in ja_corretos:
        print(
            f"{item['hostname']} [{item['tipo']}]: "
            f"{item['patrimonio']} [CORRETO]"
        )

    print("\n--- EQUIPAMENTOS IGNORADOS ---")

    for host in ignorados:
        print(f"{host} [IGNORADO]")

    print("\n===== RESUMO FINAL =====")

    print(f"Equipamentos analisados: {analisados}")
    print(f"Equipamentos especiais: {especiais}")
    print(f"Atualizações previstas: {len(alteracoes)}")
    print(f"Patrimônios corretos: {corretos}")
    print(f"Ignorados: {len(ignorados)}")
    print(f"Pendências: {len(pendencias)}")
    print(f"Falhas: {len(falhas)}")


if __name__ == "__main__":
    main()