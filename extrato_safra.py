from pathlib import Path
import pandas as pd

# def encontra_arquivos() -> list[Path]:
#     """Procura arquivos que começam com 'boletos dda' em uma estrutura de diretórios."""
#     caminho_base = Path(
#         R"\\portaarquivos\Agenda\TESOURARIA\CONTAS A PAGAR\Conciliação DDA\2025"
#     )
#     # caminho_base = Path(
#     #     R"C:\\Users\\pedro.bertoldo\\Desktop\\Pasta_teste"
#     # )

#     result:list = []
#     for pasta, _, lista_arquivos in caminho_base.walk(top_down=False):
#         for arquivo in lista_arquivos:
#             if arquivo.lower().startswith("boletos dda"):
#                 caminho_completo = Path(pasta) / arquivo
#                 result.append(caminho_completo)

#     return result

def padronizar_tabelas(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza as colunas e formatação da tabela importada."""
    print("Padronizando Safra DDA")

    # Remove as primeiras 9 linhas (cabeçalho e informações adicionais)
    indices = list(range(9))
    df.drop(indices, inplace=True)

    # Redefine as colunas com base na nova primeira linha
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # Formata colunas numéricas e ajusta precisão
    df["Valor Total (R$)"] = pd.to_numeric(df["Valor Total (R$)"], errors="coerce").round(2)
    df["Nominal (R$)"] = pd.to_numeric(df["Nominal (R$)"], errors="coerce").round(2)

    # Remove caracteres não numéricos da coluna 'Nº documento'
    df["Nº documento"] = df["Nº documento"].str.replace(r'\D', '', regex=True)

    # Ordena o DataFrame por valor nominal
    df.sort_values(by="Nominal (R$)", ascending=False, inplace=True)
    
    df["desconto"] = df["Nominal (R$)"] - df["Valor Total (R$)"]

    return df

def filtro_data(df: pd.DataFrame, data: str) -> pd.DataFrame:
    """Filtra o DataFrame por uma data específica na coluna 'Vencimento'."""
    try:
        df["Vencimento"] = pd.to_datetime(df["Vencimento"], format="%d/%m/%Y", errors="coerce")
    except Exception as e:
        raise ValueError(f"Erro ao converter datas na coluna 'Vencimento': {e}")

    data_filtro = pd.to_datetime(data, format="%d-%m-%Y", errors="coerce")
    if data_filtro is pd.NaT:
        raise ValueError(f"A data de filtro '{data}' não é válida. Use o formato 'DD-MM-YYYY'.")

    # Filtra as linhas pela data de vencimento
    df_filtrado = df[df["Vencimento"] == data_filtro]

    return df_filtrado

def execute(data: str, arquivo:Path) -> pd.DataFrame:
    """Executa o fluxo completo de processamento e filtra os dados por uma data especificada."""
    df_rel_final = pd.DataFrame()

    #arquivos = encontra_arquivos()
    #for arquivo in arquivos:
    
    print(f"Processando arquivo: {arquivo}")
    df_bruto = pd.read_excel(arquivo)

    # Padroniza as tabelas
    try:
        df_padronizado = padronizar_tabelas(df_bruto)
    except Exception as e:
        print(f"Erro ao padronizar o arquivo {arquivo}: {e}")
        # continue

    df_rel_final = pd.concat([df_rel_final, df_padronizado], ignore_index=True)
       
    if df_rel_final.empty:
        raise ValueError("Nenhum dado processado nos arquivos encontrados.")

    # Filtra os dados pela data especificada
    try:
        df_filtrado = filtro_data(df_rel_final, data)
    except ValueError as e:
        raise ValueError(f"Erro ao filtrar dados: {e}")

    return df_filtrado

# if __name__ == "__main__":
#     execute("01-05-2025","\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025\\05-MAIO\\Boletos DDA 0105.xlsx")
