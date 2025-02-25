import relat_anita as ra
import extrato_safra as es
import pandas as pd
import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from pathlib import Path
import pyfiglet

def conciliacao_DDA(rel_safra: pd.DataFrame, rel_anita: pd.DataFrame):

    rel_safra["Nominal (R$)"] = (
        rel_safra["Nominal (R$)"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)
    rel_anita["SALDO"] = (
        rel_anita["SALDO"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)
    
    conciliado = rel_safra.merge(rel_anita, left_on="Nominal (R$)", right_on="SALDO", how="outer")

    # conciliado = pd.concat(
    #     [
    #         rel_safra.sort_values("Nominal (R$)",ascending=False).reset_index(drop=True),
    #         rel_anita.sort_values("SALDO",ascending=False).reset_index(drop=True),
    #     ],
    #     axis=1,
    # )

    conciliado = conciliado.reindex(columns=['Nominal (R$)','SALDO']).sort_index(ascending=False)
    # conciliado['Diferença'] = (conciliado['Nominal (R$)'] - conciliado['SALDO']).round(2)
    # conciliado["Conciliado"] = conciliado["Diferença"] == 0
    conciliado["Conciliado"] = [f"=IF(A{i}=B{i},TRUE,FALSE)" for i in range(2, len(conciliado) + 2)]

    return conciliado

def main():

    print(pyfiglet.figlet_format("DDA\nAutomatizado\n", font="slant"))
    
    # data: pd.Timestamp = pd.to_datetime(
    #     "15-01-2025", dayfirst=True
    # )
        
    print("\nLista de Extratos encontrados do Safra...\n")
    [print(f">> {arquivo.name}") for arquivo in es.encontra_arquivos() ]
    
    data: pd.Timestamp = pd.to_datetime(
        input("\nDigite a data de vencimento...\nNo padrão: dd-mm-aaaa\n"), dayfirst=True
    )
    
    print(f"Data Procurada: {data.strftime("%d-%m-%Y")}\n")

    df_safra = es.execute(
        data.strftime("%d-%m-%Y")
    )  # Busca em padrão brasileiro de datas
    df_anita = ra.execute(
        data.strftime("%Y-%m-%d")
    )  # Busca em padrão Americano de datas

    print("Processando...\n")
    conciliado = conciliacao_DDA(df_safra, df_anita)

    print(f"Tabela Final\n{conciliado}")

    nome_arquivo = f"relatorio_{data.strftime("%d-%m-%Y")}.xlsx"
    
    caminho_saida = Path(f"ALGUM CAMINHO\\{nome_arquivo}")

    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
        df_safra.to_excel(writer, sheet_name="Safra", index=False)
        df_anita.to_excel(writer, sheet_name="Anita", index=False)
        conciliado.to_excel(writer, sheet_name="Conciliado", index=False)
    print("Concluido! ;)\n")
    
    input("Pressione ENTER tecla para sair...")

if __name__ == "__main__":
    main()