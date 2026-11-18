# 🚀 Milvus Inventory Automation

**Python | REST API | IT Automation | Asset Management**

Automação desenvolvida em **Python** para gerenciamento de inventário de TI por meio da API REST do **Milvus Service Desk**.

O projeto permite consultar equipamentos, validar grupos, identificar inconsistências e automatizar atualizações, reduzindo processos manuais e aumentando a confiabilidade dos dados.

## ⚙️ Funcionalidades

- **GET:** Consulta paginada de equipamentos e identificação dos grupos.
- **PUT:** Atualização automática de grupos conforme regras de negócio.
- **Validação:** Comparação entre grupo atual e grupo esperado.
- **Simulação:** Visualização das alterações antes da execução real.
- **Auditoria:** Registro de atualizações e tratamento de inconsistências.
- **Segurança:** Proteção de equipamentos com grupos não identificados.

## 🛠️ Tecnologias

`Python 3` · `REST API` · `Requests` · `JSON` · `python-dotenv` · `Git`

## 📁 Estrutura do projeto

```text
milvus-inventory-automation/
├── Config/
│   ├── conexao.py
│   ├── dicionario.py
│   └── log.py
├── Services/
│   ├── GET.py
│   └── post.py
├── Data/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## 💻 Exemplos de uso

### 1. Menu principal

```text
===== MILVUS | INTEGRAÇÃO PYTHON =====

[1] Consultar inventário (GET)
[2] Atualizar grupos (PUT)
[3] Consultar histórico de atualizações
[0] Sair

Selecione uma opção:
```

### 2. Consulta de inventário (GET)

```text
===== RESULTADO GET =====

Equipamentos encontrados: 325
Com grupo identificado: 323
Com ID, mas sem nome: 2
Sem grupo atribuído: 0
Grupos disponíveis: 191

Arquivo: dados.json
Status: Concluído com sucesso.
```

### 3. Validação e atualização (PUT)

```text
===== RESULTADO PUT =====

Modo: SIMULAÇÃO
Equipamentos corretos: 315
Precisam de alteração: 1
Sem regra definida: 7
Grupos não identificados: 2
Falhas: 0

--- ALTERAÇÕES ---
HOSTNAME: Grupo atual -> Grupo destino [PENDENTE]
```

Os resultados são exemplos de execução em ambiente de teste. Nenhuma alteração é realizada no modo de simulação.

### 4. Exportação JSON

Exemplo simplificado de equipamento consultado:

```json
{
  "id": 123456,
  "hostname": "PC-001",
  "apelido": "ZZ EMP - ACC - Usuario Exemplo",
  "tipo_dispositivo_text": "Notebook",
  "grupo_dispositivo_id": 32789,
  "grupo": "Accenture-ACC"
}
```

Os equipamentos cujos grupos não forem identificados são registrados separadamente em `nao_identificados.json`, sem atualização automática.

## 🚀 Instalação e execução

**1. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**2. Configure o arquivo `.env`** com as credenciais e tokens necessários para autenticação nas APIs.

**3. Execute a aplicação:**

```bash
python main.py
```

## 🔐 Segurança

O projeto utiliza variáveis de ambiente para autenticação, validação de cliente, modo de simulação e confirmação manual antes de operações reais.

Credenciais, logs e informações internas do inventário devem permanecer fora do versionamento público.

## 👨‍💻 Autor

**Vinícius Zile Costa**

Analista de TI | Python | SQL | Microsoft 365 | Active Directory | Entra ID

---

⭐ **Projeto de automação e integração de sistemas aplicado à gestão de ativos e infraestrutura de TI.**
