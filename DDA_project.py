import relat_anita as ra
import extrato_safra as es
import pandas as pd

def main():
    
    data:pd.Timestamp = pd.to_datetime(input("Digite a data de vencimento:\n {dd/mm/aaaa} \n"),dayfirst=True)
    print(f"Data Procurada: {data.strftime("%d-%m-%Y")}")
    
    df_safra = es.execute(data.strftime("%d-%m-%Y")) #Busca em padrão brasileiro de datas
    df_anita = ra.execute(data.strftime("%Y-%m-%d")) #Busca em padrão Americano de datas
    
    print(df_safra)
    print(df_anita)

if __name__ == "__main__":
    main()