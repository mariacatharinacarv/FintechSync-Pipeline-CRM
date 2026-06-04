# 🚀 FintechSync: Pipeline de Data Driven CRM (Fase 1)

## 📌 Sobre o Projeto
Este projeto simula um cenário real de engenharia e inteligência de dados em uma Fintech de contas digitais. O objetivo principal foi construir um pipeline automatizado que integra dados transacionais brutos armazenados na nuvem a regras de negócio voltadas para estratégias de **CRM (Customer Relationship Management)**, identificando oportunidades de engajamento e mitigação de risco de perda de clientes.

A arquitetura do projeto aplica o conceito de **Reverse ETL**, onde os dados processados e refinados localmente são devolvidos ao Data Warehouse centralizado para alimentar ferramentas de automação de marketing e CRM (como Braze, Salesforce ou Hubspot).

---

## 🛠️ Tecnologias Utilizadas
* **Snowflake Data Warehouse:** Armazenamento centralizado, modelagem relacional e processamento em nuvem.
* **Python:** Linguagem base para construção do pipeline de dados.
* **Pandas:** Biblioteca utilizada para manipulação de DataFrames, agregações temporais e aplicação de lógicas de negócio.
* **Snowflake Connector para Python (com extensão PyArrow):** Ponte de comunicação de alta performance para extração e carga de dados via código.

---

## 📊 Arquitetura do Pipeline

1. **Camada de Origem (Snowflake SQL):** Criação das tabelas de cadastro de clientes (`TABELA_CLIENTES`) e o log transacional bruto (`TABELA_TRANSACOES`), simulando o comportamento de uso do aplicativo (PIX, Cartão, Boleto).
2. **Camada de Extração (Python):** Conexão segura e extração das transações brutas direto para um DataFrame do Pandas.
3. **Camada de Inteligência (Pandas):** Consolidação dos dados transacionais por cliente para calcular:
    * **Recência (Dias Inativo):** Diferença de tempo entre a última movimentação e a data atual.
    * **Métrica de Churn:** Atribuição da flag `ALERTA_CHURN` para clientes sem movimentação há mais de 30 dias (foco em retenção).
    * **Métrica de Crédito:** Atribuição da flag `UPGRADE_CREDITO` para clientes com movimentações consolidadas acima de R$ 3.000,00 (foco em cross-sell/upsell).
4. **Camada de Carga / Reverse ETL (Snowflake):** Gravação do resultado final na tabela otimizada `CRM_CUSTOMER_360` diretamente via Python utilizando a função de alta performance `write_pandas`.

---

## 💻 Como Executar o Projeto

1. Execute o script contido em `schema.sql` dentro do console do seu Snowflake para estruturar o banco de dados.
2. Instale as dependências necessárias no seu ambiente Python local:
   ```bash
   pip install "snowflake-connector-python[pandas]"
