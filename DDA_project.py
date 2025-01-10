import relat_anita as ra
import extrato_safra as es
import pandas as pd
import openpyxl

def conciliacao_DDA(rel_safra:pd.DataFrame,rel_anita:pd.DataFrame):
    
    rel_safra['Nominal (R$)'] = rel_safra['Nominal (R$)'].replace(',', '.', regex=True).astype(float).round(2)
    rel_anita['SALDO'] = rel_anita['SALDO'].replace(',', '.', regex=True).astype(float).round(2)
    conciliado = rel_safra.merge(rel_anita, left_on="Nominal (R$)", right_on="SALDO", how="outer").sort_values(by='SALDO',ascending=False)
    conciliado = conciliado.reindex(columns=['Nominal (R$)','SALDO'])
    conciliado['Diferença'] = conciliado['Nominal (R$)'] - conciliado['SALDO']

    return conciliado

def main():
    
    data:pd.Timestamp = pd.to_datetime(input("Digite a data de vencimento:\n {dd/mm/aaaa} \n"),dayfirst=True)
    print(f"Data Procurada: {data.strftime("%d-%m-%Y")}")
    
    df_safra = es.execute(data.strftime("%d-%m-%Y")) #Busca em padrão brasileiro de datas
    df_anita = ra.execute(data.strftime("%Y-%m-%d")) #Busca em padrão Americano de datas
    
    conciliado = conciliacao_DDA(df_safra,df_anita)

    conciliado.to_clipboard(excel=True)

    # with pd.ExcelWriter("relatorios.xlsx", engine="openpyxl") as writer:
    #     df_safra.to_excel(writer, sheet_name="Safra", index=False)
    #     df_anita.to_excel(writer, sheet_name="Anita", index=False)
    #     conciliado.to_excel(writer, sheet_name="Conciliado", index=False)
        

if __name__ == "__main__":
    main()