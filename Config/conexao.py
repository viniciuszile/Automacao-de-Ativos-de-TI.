
import os
import requests

from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

BASE_URL = "https://apiintegracao.milvus.com.br/api"
TOKEN = os.getenv("MILVUS_API_TOKEN")


def conectar():
    """Estabelece conexão com a API do Milvus."""

    if not TOKEN:
        raise ValueError("Token Milvus não encontrado no .env")

    # Cria a sessão autenticada.
    sessao = requests.Session()

    sessao.headers.update({
        "Authorization": TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json"
    })

    # Repete requisições GET em falhas temporárias.
    retry = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True
    )

    sessao.mount("https://", HTTPAdapter(max_retries=retry))

    # Valida a conexão com o Milvus.
    resposta = sessao.get(
        f"{BASE_URL}/cliente/busca",
        timeout=30
    )

    resposta.raise_for_status()

    print("Conexão com Milvus estabelecida!")

    return sessao
