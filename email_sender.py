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

PATH_LOCAL = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Config.settings")
django.setup()

# PASTA_ENTRADA = Path(
#     f"\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025\\RelatórioDDA"
# )  # official
PASTA_ENTRADA = Path(
    f"C:\\Users\\pedro.bertoldo\\Desktop\\Pasta_teste"
)  # Teste

PADRAO_NOME = re.compile(r"^relatorio_\d{2}-\d{2}-\d{4}.xlsx$", re.IGNORECASE)

def mini_filtro(df: pd.DataFrame):
    
    pos_para_mari = df.columns.get_loc("para_maristela")
    pos_para_loja = df.columns.get_loc("para_loja")
    
    for idx, linha in df.iterrows():
        
        valor_x = linha.iat[pos_para_mari]
        valor_n = linha.iat[pos_para_loja]
        
        if str(valor_x).strip().lower() == "x":
            print("para_mari")
            mari = df[df["para_maristela"].astype(str).str.lower() == "x"]

            with tempfile.TemporaryDirectory() as tmp_dir:
            
                tmp_dir = Path(tmp_dir) / "verificar_lancamento.xlsx"
                mari.to_excel(tmp_dir, index=False)

                subject="EMAIL_MARISTELA"
                body="AAAAAAAA"
                # to_maristela = ["maristela@balaroti.com.br"]
                to = ["pedro.bertoldo@balaroti.com.br"]
                cc=[""]
                
                enviar_email(subject,body,to,cc,attachments=[tmp_dir])    
            
            continue
        
        if valor_n.is_integer():
            print(f"para_loja: {int(valor_n)}")
            
            linha_loja = df[df["para_loja"] == int(valor_n)]
            
            loja_ite = int(valor_n)
            email_gerente = lojas_emails.get(loja_ite)
            
            if email_gerente == "?" or email_gerente == None:
                print("Email não cadastrado")
                continue
            else:
                with tempfile.TemporaryDirectory() as tmp_dir:
                
                    tmp_dir = Path(tmp_dir) / f"verificar_loja_{int(valor_n)}.xlsx"
                    linha_loja.to_excel(tmp_dir, index=False)

                    subject=f"EMAIL_LOJA_{int(valor_n)}"
                    body="IIIIIIIII"
                    to = email_gerente
                    cc=[""]
                    
                    enviar_email(subject,body,to,cc,attachments=[tmp_dir])
                    
                    continue

            continue


def mini_processador(caminho: Path = PASTA_ENTRADA):

    for dirpath, _, files in os.walk(caminho):
        for file in files:
            if PADRAO_NOME.match(file):
                file_path = Path(dirpath) / file
                print(file_path)
                df = pd.read_excel(file_path,sheet_name="Conciliado")
                mini_filtro(df)
                

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

if __name__ == "__main__":
    mini_processador()