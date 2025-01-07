import relat_anita as ra
import extrato_safra as es

def main():
    
    df_safra = es.execute()
    
    # data:pd.Timestamp = pd.to_datetime(input("Digite a data de vencimento:\n {dd/mm/aaaa} \n"),format="%d-%m-%Y")
    # data = data.strftime("%Y-%m-%d")
    data: str = "2025-01-03"
    df_anita = ra.execute(data)

    print(df_safra)
    print(df_anita)

if __name__ == "__main__":
    main()