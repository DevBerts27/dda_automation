import django
import os
from django.core.mail import EmailMessage, get_connection
from django.core import mail
from django.core.mail import send_mail
from pathlib import Path
import Config.settings as settings
import pandas as pd
import re
import tempfile
from dict_lojas_emails import lojas_emails
import Database.BD_cache as bd
from datetime import datetime as dt

PATH_LOCAL = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Config.settings")
django.setup()

ANO = dt.today().year

PASTA_ENTRADA = Path(
    f"\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\{ANO}\\RelatórioDDA\\_pronto_enviar_email"
)  # official
# PASTA_ENTRADA = Path(
#     f"C:\\Users\\pedro.bertoldo\\Desktop\\Pasta_teste"
# )  # Teste

PADRAO_NOME = re.compile(r"^relatorio_\d{2}-\d{2}-\d{4}.xlsx$", re.IGNORECASE)
DATA_ARQUIVO_REGEX = re.compile(r"(\d{2}-\d{2}-\d{4})",re.IGNORECASE)
NOME_TABELA_BANCO = "execucoes_email"

def enviar_email(subject: str, body: str, to: list, cc=None, attachments=None):
    with mail.get_connection() as conn:
        conn = get_connection()
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="Financeiro_bot",
            to=to,
            cc=cc,
            connection=conn,
        )

        if attachments:
            for attachment in attachments:
                email.attach_file(attachment)
        conn.open()
        sent = conn.send_messages([email])
        conn.close()
        print("Email enviado com sucesso!")

def pipeline(df: pd.DataFrame, data_arquivo):

    mari = df[df["para_maristela"].astype(str).str.lower() == "x"]

    if mari.empty:
        print("Nada para enviar para a Maristela...")
        
    else:
        
        print("Enviando para Maristela")
        with tempfile.TemporaryDirectory() as tmp_dir:
        
            tmp_dir = Path(tmp_dir) / f"lancamentos_{data_arquivo}.xlsx"
            mari.to_excel(tmp_dir, index=False)

            subject="Verificar lancamençentos"
            body=f"""Olá \nSegue em anexo lançamentos do dia {data_arquivo} para verificar.
            \nResponder para financeiro@balaroti.com.br"""
            to = ["maristela@balaroti.com.br","rosi.santos@balaroti.com.br","aline.rodrigues@balaroti.com.br"]
            cc=["financeiro@balaroti.com.br","pedro.bertoldo@balaroti.com.br"]
            
            enviar_email(subject,body,to,cc,attachments=[tmp_dir])    


    pos_para_loja = df.columns.get_loc("para_loja")
    
    valor_lista:list[int] = []
    
    for _, linha in df.iterrows():
        
        valor_n = linha.iat[pos_para_loja]
        if valor_n.is_integer():
            valor_lista.append(valor_n)
    
    valor_lista = list(set(valor_lista))
    
    for valor_n_iter in valor_lista:
        
        if valor_n_iter.is_integer():
            print(f"para_loja: {int(valor_n_iter)}")

            linha_loja = df[df["para_loja"] == int(valor_n_iter)]
            
            loja_ite = int(valor_n_iter)
            email_gerente = lojas_emails.get(loja_ite)
            
            if email_gerente == "?" or email_gerente == None:
                print("Email não cadastrado")
                continue
            else:
                with tempfile.TemporaryDirectory() as tmp_dir:
                
                    tmp_dir = Path(tmp_dir) / f"Lançamentos_{data_arquivo}.xlsx"
                    linha_loja.to_excel(tmp_dir, index=False)

                    subject=f"Verificar Lançamento Loja:{int(valor_n_iter)}"
                    body=f"""Olá Loja {int(valor_n_iter)}
                    \nPoderia verificar este lançamento em anexo ?\nResponder para financeiro@balaroti.com.br"""
                    to = email_gerente
                    cc=["financeiro@balaroti.com.br","pedro.bertoldo@balaroti.com.br"]
                    
                    enviar_email(subject,body,to,cc,attachments=[tmp_dir])
                    
                    continue

            continue

def main(caminho: Path = PASTA_ENTRADA):

    if not bd.banco_existe(NOME_TABELA_BANCO):
        bd.criar_tabela(NOME_TABELA_BANCO)
    
    for dirpath, _, files in os.walk(caminho):
        for file in files:
            
            if PADRAO_NOME.match(file):
                
                if file not in bd.carregar_log(NOME_TABELA_BANCO):
                    
                    file_path = Path(dirpath) / file

                    match = re.search(DATA_ARQUIVO_REGEX, file)
                    data_arquivo_str = match.group(1)

                    df = pd.read_excel(file_path,sheet_name="Conciliado")
                    pipeline(df,data_arquivo_str)

                    bd.salvar_no_log(file,NOME_TABELA_BANCO)
                
                print(f"Arquivo já processado: {file}")
                
                continue


if __name__ == "__main__":
    main()