import pyodbc
import pandas as pd
import datetime

DIAS_PLUS = 5

QUERY = """
SELECT
    DDA_DATA_ARQ AS DDA_DATA_ARQUIVO,
    DDA_SEQ_REG AS SEQ_REG,
    DDA_FORNE AS COD_FORNECEDOR,
    DDA_NOTA AS NOTA,
    DDA_PARTE AS PARTE,
    DDA_VENCTO AS DDA_DATA_VENCIMENTO,
    DDA_ITAU_DT_LOTE AS LOTE,
    DDA_ITAU_DT_CODBAR AS COD_BARRA,
    DDA_ITAU_DT_NOME_CEDENTE AS NOME_CEDENTE,
    DDA_ITAU_DT_VALOR_NOMINAL AS VALOR,
    DDA_ITAU_DT_NRDOC AS N_DOCUMENTO,
    DDA_ITAU_DT_DTEMIS AS DT_EMISSAO,
    DDA_ITAU_DT_JUROS AS JUROS,
    DDA_ITAU_DT_DTLIM_1DESC AS DT_LIMITE_DESC,
    DDA_ITAU_DT_VLR_1DESC AS VALOR_DESCONTO,
    DDA_ITAU_DT_DTLIM_PGTO AS DT_PGTO_LIMITE
FROM MOVDDA
WHERE DDA_VENCTO BETWEEN ? AND ?
"""

def relat_adv(data_rel: str) -> pd.DataFrame:
    conn_str = "DSN=XDBBALA"
    try:
        with pyodbc.connect(conn_str) as conn:
            cur = conn.cursor()
            # Converta para datetime.date antes de executar
            dt_param = datetime.datetime.strptime(data_rel, "%Y-%m-%d").date()
            dt_param_plus_5 = dt_param + datetime.timedelta(days=DIAS_PLUS)
            print(f"Busca por: {dt_param} até {dt_param_plus_5}")
            cur.execute(QUERY, dt_param, dt_param_plus_5)

            # Revele quais colunas vieram mesmo
            cols = [c[0] for c in cur.description]
            print("Colunas retornadas:", cols)

            rows = cur.fetchall()
            return pd.DataFrame.from_records(rows, columns=cols)

    except pyodbc.Error as err:
        print("Erro ODBC:", err)
        return pd.DataFrame()

def formata_df(df: pd.DataFrame) -> pd.DataFrame:
    # Só tente converter se a coluna existir
    for col in ("DDA_DATA_ARQUIVO","DDA_DATA_VENCIMENTO"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            
    for col in ("VALOR_DESCONTO","JUROS","VALOR"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])
    
    for col in ("DT_EMISSAO","DT_LIMITE_DESC","DT_PGTO_LIMITE"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col].astype(str).str.zfill(0),format="%Y%m%d", errors="coerce")
    
    df["VALOR_LIQ"] = (df["VALOR"] - df["VALOR_DESCONTO"]).round(2)
    
    df["VALOR_LIQ"].round(2)
    
    return df

def execute(data_rel:str):
    df = relat_adv(data_rel)
    if df.empty:
        # print("Nenhum dado para", data_rel)
        return df
    return formata_df(df)

# if __name__ == "__main__":
#     resultado = execute("2025-06-30")
#     print(resultado.head())