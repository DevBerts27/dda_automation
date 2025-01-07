import os
from pathlib import Path
import pandas as pd


def encontra_arquivos():
    caminho_base = Path(
        R"\\portaarquivos\Agenda\TESOURARIA\CONTAS A PAGAR\Conciliação DDA\2025\01 - JANEIRO"
    )

    caminho = caminho_base

    result = []
    for pasta, _, lista_arquivos in caminho.walk():
        for arquivo in lista_arquivos:
            nome_arquivo = arquivo.lower()
            if nome_arquivo.startswith("boletos dda"):
                caminho_completo = pasta / arquivo
                result.append(caminho_completo)

    return result


def padronizar_tabelas(df: pd.DataFrame):

    print("Padronizando Safra DDA")
    indices = list(range(9))
    df.drop(indices, inplace=True)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    df["Valor Total (R$)"] = df["Valor Total (R$)"].astype(float).round(2)
    df["Nominal (R$)"] = df["Nominal (R$)"].astype(float).round(2)

    return df


def execute():

    df_rel_final = pd.DataFrame()

    arquivos = encontra_arquivos()
    print(arquivos)

    for arquivo in arquivos:
        print(f"Processando arquivo: {arquivo}")
        df_bruto = pd.read_excel(arquivo)
        df_padronizado = padronizar_tabelas(df_bruto)
        df_rel_final = pd.concat([df_rel_final, df_padronizado], ignore_index=True)

    print("\nDataFrame Final Mesclado:")
    print(df_rel_final)

    return df_rel_final


if __name__ == "__main__":
    execute()
