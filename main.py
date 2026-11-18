from Services.GET import main as executar_get
from Services.post import main as executar_post
from Config.log import exibir_resumo

opcoes = {
    "1": executar_get,
    "2": executar_post,
    "3": exibir_resumo
}

def main():
    while True:
        print("""
===== MILVUS | INTEGRAÇÃO PYTHON =====
[1] Consultar inventário (GET)
[2] Atualizar grupos (PUT)
[3] Consultar histórico de atualizações
[0] Sair
""")

        opcao = input("Selecione uma opção: ").strip()

        if opcao == "0":
            print("Encerrando aplicação...")
            break

        if opcao not in opcoes:
            print("Opção inválida.")
            continue

        try:
            opcoes[opcao]()
        except Exception as erro:
            print(f"Erro na execução: {erro}")

        input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    main()
