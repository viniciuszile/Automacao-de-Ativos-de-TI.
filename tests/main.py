
# from Config.conexao import conectar
# # import GET.dispositivos as dispositivos


# def main():
#     # Estabelece a conexão autenticada com o Milvus.
#     api = conectar()

#     # Configura tentativas automáticas em falhas temporárias.
#     api = dispositivos.configurar_tentativas(api)

#     # Consulta notebooks e desktops da Runtalent.
#     dados = dispositivos.consultar_dispositivos(api)

#     # Recupera os grupos disponíveis.
#     grupos = dispositivos.consultar_grupos()

#     # Consulta patrimônio e grupo de cada equipamento.
#     completos = dispositivos.enriquecer_dispositivos(
#         api, dados["lista"], grupos
#     )

#     # Salva o JSON e apresenta o resumo final.
#     dispositivos.salvar_json(completos)
#     dispositivos.exibir_dispositivos(completos)


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as erro:
#         print(f"Erro na aplicação: {erro}")
