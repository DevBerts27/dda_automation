import pandas as pd
import pyodbc
import numpy as np
import senhas as se

QUERY = """
SELECT
    AP_NOTA AS NOTA,
    AP_TIPO AS TIPO,
    AP_PARTE AS PARTE,
    AP_CODFOR AS COD_FORNECEDOR,
    AP_BOLETO AS BOLETO,
    AP_NOMEFOR AS NOME_FORNECEDOR,
    AP_DATAV,
    AP_VALOR AS VALOR,
    AP_DESC AS DESCONTO,
    AP_VALORDEV AS DEVOLUCAO,
    AP_LOJA AS LOJA,
    CASE WHEN AP_BOLETO = '' OR AP_BOLETO IS NULL THEN 'N' WHEN AP_ESPECIE NOT IN ('C') THEN 'B' WHEN AP_ESPECIE = 'C' THEN 'C' END AS BNC
FROM A_PAGAR 
WHERE AP_DATAV = ?
ORDER BY VALOR DESC
FOR BROWSE
"""

# Query feita para pegar apenas os dados necessários do anita...
def rel_anita(data_rel: str) -> pd.DataFrame:
    """Busca no Banco de dados as colunas que serão usadas para fazer o DDA
    Em poucas palavras é o relatório do Anita...

    Args:
        data_rel (str): Input da data desejada para SELECT no Banco de dados.

    Returns:
        pd.DataFrame: Dataframe Retornado com o relatório do Anita.
    """
    try: 
        url_conexao = se.url_conexao
        
        # Gerenciamento de conexão com `with`
        with pyodbc.connect("DSN=BDMTRIZ") as conexao: 
            res = conexao.cursor().execute(QUERY, data_rel)
            # Criar DataFrame a partir dos resultados
            df = pd.DataFrame(
                map(list, res), columns=[desc[0] for desc in res.description]
            )
            print("Extraindo relatórios do DB")
            # Verificar se há dados
            if df.empty:
                print("Nenhum dado encontrado")
                return pd.DataFrame(columns=[desc[0] for desc in res.description])
            return df

    except pyodbc.Error as erro:
        print(f"Erro na execução da consulta: {erro}")
        return pd.DataFrame()

def formata_df(df: pd.DataFrame):
    """Apenas formata o que foi a consulta do DataFrame
    Args:
        df (pd.DataFrame): Argumento, DataFrame da consulta SQL.
    Returns:
        _type_: pd.DataFrame
    """

    df["SALDO"] = df["VALOR"] - df["DESCONTO"] - df["DEVOLUCAO"]

    df['NRO.BOL'] = df['NOTA'].astype(str) + df['TIPO'].astype(str) + df['PARTE'].astype(str)
    
    df_filtrado = df[df["BNC"] == 'N']
    
    print(df_filtrado)
    
    return df_filtrado

def execute(data:str):
    
    df = rel_anita(data)
    df_format =formata_df(df)
    
    return df_format
    
# if __name__ == "__main__":
#     execute("2025-01-31")