# 🚀 Milvus Inventory Automation

**Python | REST API | IT Automation | Asset Management**

Automação desenvolvida em **Python** para gerenciamento de inventário de TI por meio da API REST do **Milvus Service Desk**.

O projeto permite consultar equipamentos, validar grupos, identificar inconsistências e automatizar atualizações, reduzindo processos manuais e aumentando a confiabilidade dos dados.

## ⚙️ Funcionalidades

- **GET:** Consulta paginada de equipamentos e identificação dos grupos.
- **PUT (Grupos):** Atualização automática de grupos conforme regras de negócio.
- **PUT (Patrimônio):** Associação automática do e-mail do colaborador ao campo `patrimonio`, utilizando hostname e dados de uma base JSON. Equipamentos especiais (`#1` a `#5`) recebem o próprio hostname como patrimônio.
- **Validação:** Comparação entre os dados atuais e os valores esperados.
- **Simulação:** Visualização das alterações antes da execução real.
- **Auditoria:** Registro de atualizações e tratamento de inconsistências.
- **Segurança:** Proteção de equipamentos com dados não identificados ou inconsistentes.

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
│   ├── post.py
│   └── put_patrimonio.py
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
[4] Atualizar patrimônio (PUT - E-mail)
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

### 3. Validação e atualização de grupos (PUT)

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

### 4. Atualização de patrimônio (PUT)

A funcionalidade utiliza uma base JSON contendo **hostname, nome e e-mail dos colaboradores** para localizar os equipamentos no inventário e atualizar o campo `patrimonio` pela API do Milvus.

Equipamentos identificados pelos prefixos `#1` a `#5` no apelido recebem o próprio hostname como patrimônio. Registros inconsistentes ou sem correspondência são separados para validação, e equipamentos definidos na lista de exclusões são ignorados.

```text
===== RESULTADO PUT PATRIMÔNIO =====

Modo: SIMULAÇÃO
Equipamentos analisados: 325
Equipamentos especiais: 29
Patrimônios já corretos: 28
Precisam de atualização: 292
Atualizações simuladas: 292
Atualizações confirmadas: 0
Ignorados: 5
Pendências: 0
Falhas: 0
```

Os resultados apresentados são exemplos de execução. Nenhuma alteração é realizada no modo de simulação.

### 5. Exportação JSON

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
