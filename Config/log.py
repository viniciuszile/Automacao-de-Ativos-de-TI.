
import json
from datetime import datetime
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "Data" / "logs_put.json"


def registrar_atualizacao(sigla, empresa, dispositivo, grupo_anterior, origem="PUT"):
    logs = (
        json.loads(ARQUIVO.read_text(encoding="utf-8"))
        if ARQUIVO.exists()
        else {"total_atualizados": 0, "total_empresas": 0, "empresas": {}}
    )

    empresas = logs["empresas"]

    if any(
        str(item["id"]) == str(dispositivo["id"])
        for dados in empresas.values()
        for item in dados["dispositivos"]
    ):
        return False

    registro = empresas.setdefault(sigla, {
        "nome": empresa["empresa"],
        "grupo": empresa["grupo"],
        "grupo_id": empresa["grupo_id"],
        "total_atualizados": 0,
        "dispositivos": []
    })

    registro["dispositivos"].append({
        "id": dispositivo["id"],
        "hostname": dispositivo.get("hostname"),
        "apelido": dispositivo.get("apelido"),
        "grupo_anterior": grupo_anterior,
        "grupo_novo": empresa["grupo_id"],
        "origem": origem,
        "data": datetime.now().isoformat(timespec="seconds")
    })

    registro["total_atualizados"] = len(registro["dispositivos"])
    logs["total_atualizados"] += 1
    logs["total_empresas"] = len(empresas)

    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(
        json.dumps(logs, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    return True


def exibir_resumo():
    if not ARQUIVO.exists():
        print("\nNenhuma atualização registrada.")
        return

    logs = json.loads(ARQUIVO.read_text(encoding="utf-8"))

    print("\n===== HISTÓRICO DE ATUALIZAÇÕES =====")
    print(f"Máquinas contabilizadas: {logs['total_atualizados']}")
    print(f"Empresas processadas: {logs['total_empresas']}")

    for sigla, empresa in logs["empresas"].items():
        print(f"{sigla} - {empresa['nome']}: {empresa['total_atualizados']} máquinas")
