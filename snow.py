import snowflake.connector
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

# 1. CONFIGURAÇÃO (Suas credenciais)
config = {
    'user': 'catharina',
    'password': '1463692544Igor',
    'account': 'yrbvbbq-cy34700',
    'warehouse': 'COMPUTE_WH',
    'database': 'FINTECH_CRM_DB',
    'schema': 'CORE_DATA'
}

# 2. EXTRAÇÃO (Busca dados da nuvem)
def conectar_e_buscar_dados():
    try:
        print("🔄 Tentando conectar ao Snowflake...")
        conn = snowflake.connector.connect(**config)
        print("🎉 Conexão realizada com sucesso!")
        
        cursor = conn.cursor()
        query = "SELECT id_cliente, valor, data_hora, categoria FROM TABELA_TRANSACOES"
        cursor.execute(query)
        
        df_transacoes = cursor.fetch_pandas_all()
        
        cursor.close()
        conn.close()
        return df_transacoes
        
    except Exception as e:
        print(f"❌ Opa, deu erro na conexão: {e}")
        return None

# 3. INTELIGÊNCIA (Aplica as regras de CRM e Churn)
def processar_regras_crm(df_transacoes):
    print("\n🧠 Processando regras de negócio para o CRM...")
    
    data_atual = pd.to_datetime('2026-06-04 16:15:00')
    df_transacoes['DATA_HORA'] = pd.to_datetime(df_transacoes['DATA_HORA'])
    
    df_crm = df_transacoes.groupby('ID_CLIENTE').agg(
        ultima_transacao=('DATA_HORA', 'max'),
        total_movimentado=('VALOR', 'sum')
    ).reset_index()
    
    df_crm['DIAS_INATIVO'] = (data_atual - df_crm['ultima_transacao']).dt.days
    df_crm['ALERTA_CHURN'] = df_crm['DIAS_INATIVO'] > 30
    df_crm['UPGRADE_CREDITO'] = df_crm['total_movimentado'] > 3000.00
    
    # Deixando o nome das colunas em MAIÚSCULO para o Snowflake aceitar nativamente
    df_crm.columns = [x.upper() for x in df_crm.columns]
    
    return df_crm

# 4. CARGA / REVERSE ETL (Salva o resultado de volta na nuvem)
def salvar_dados_no_snowflake(df_crm):
    try:
        print("\n📤 Enviando a tabela final de volta para o Snowflake...")
        conn = snowflake.connector.connect(**config)
        
        # Envia os dados e cria a tabela automaticamente se não existir
        sucesso, n_chunks, n_rows, _ = write_pandas(
            conn=conn,
            df=df_crm,
            table_name='CRM_CUSTOMER_360',
            auto_create_table=True,
            overwrite=True
        )
        
        conn.close()
        if sucesso:
            print(f"🎉 Sucesso! {n_rows} linhas salvas na tabela 'CRM_CUSTOMER_360' lá na nuvem!")
            
    except Exception as e:
        print(f"❌ Erro ao salvar no Snowflake: {e}")

# 5. O MAESTRO (Dita a ordem em que o pipeline deve rodar)
if __name__ == "__main__":
    # Passo A: Puxa o bruto
    dados_brutos = conectar_e_buscar_dados()
    
    if dados_brutos is not None:
        # Passo B: Calcula Churn e Upgrade
        tabela_final = processar_regras_crm(dados_brutos)
        
        print("\n--- 🔥 TABELA FINAL PRONTA PARA O CRM ---")
        print(tabela_final[['ID_CLIENTE', 'DIAS_INATIVO', 'ALERTA_CHURN', 'UPGRADE_CREDITO']])
        
        # Passo C: Guarda na Nuvem
        salvar_dados_no_snowflake(tabela_final)
