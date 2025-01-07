import pandas as pd
import pyodbc
import numpy as np
import senhas as se

QUERY = """
SELECT
    AP_NOTA AS NOTA,
    AP_DUPL AS DUPLICATA,
    AP_TIPOCOMPROMISSO AS TIPO,
    AP_CODFOR AS COD_FORNECEDOR,
    AP_NOMEFOR AS NOME_FORNECEDOR,
    AP_DATAV AS DATA_VENCIMENTO,
    AP_NCBOLETO AS BOLETO,
    COALESCE(AP_BAIXA_MANUAL, '') AS AP_BAIXA_MANUAL,
    COALESCE(AP_ESPECIE, '') AS AP_ESPECIE,
    AP_VALOR AS VALOR,
    AP_DESC AS DESCONTO,
    AP_LOJA AS LOJA
FROM A_PAGAR 
WHERE AP_DATAV = ?
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
        with pyodbc.connect(url_conexao) as conexao:
            res = conexao.cursor().execute(QUERY, data_rel)
            # Criar DataFrame a partir dos resultados
            df = pd.DataFrame(
                map(list, res), columns=[desc[0] for desc in res.description]
            )
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
    df["BNC"] = df["AP_BAIXA_MANUAL"].fillna("") + df["AP_ESPECIE"].replace(
        "X", np.nan
    ).fillna("")
    df.drop(["AP_BAIXA_MANUAL", "AP_ESPECIE"], axis=1, inplace=True)
    df["BOLETO"].fillna("")

    return df

def execute(data:str):
    
    df = rel_anita(data)
    df_format =formata_df(df)
    
    return df_format
    
# if __name__ == "__main__":
#     execute()