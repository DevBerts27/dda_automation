import os
from pathlib import Path
from typing import List
import time
import threading

import pandas as pd
import pyfiglet
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import extrato_safra as es
import relat_anita as ra
import BD_cache as bd

class PastaVigiaHandler(FileSystemEventHandler):
    def __init__(self, filtros: List[str], acao):
        self.filtros = filtros
        self.acao = acao

    def on_created(self, event):
        if not event.is_directory:
            _, extensao = os.path.splitext(event.src_path)
            if extensao in self.filtros:
                print(f"Novo arquivo detectado: {event.src_path}")
                # Inicia o processamento em uma thread separada para não bloquear o watcher
                threading.Thread(target=self.acao, args=(event.src_path,)).start()

def conciliacao_DDA(rel_safra: pd.DataFrame, rel_anita: pd.DataFrame):
    rel_safra["Nominal (R$)"] = (
        rel_safra["Nominal (R$)"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)
    rel_anita["SALDO"] = (
        rel_anita["SALDO"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)
    
    conciliado = rel_safra.merge(rel_anita, left_on="Nominal (R$)", right_on="SALDO", how="outer")
    conciliado = conciliado.reindex(columns=['Nominal (R$)','SALDO']).sort_index(ascending=False)
    conciliado["Conciliado"] = [f"=IF(A{i}=B{i},TRUE,FALSE)" for i in range(2, len(conciliado) + 2)]
    return conciliado

def vigiar_pasta(caminho_pasta: str, filtros: List[str]):
    observador = Observer()
    evento_handler = PastaVigiaHandler(filtros=filtros, acao=minha_acao)
    observador.schedule(evento_handler, caminho_pasta, recursive=False)

    print(f"Vigiando a pasta: {caminho_pasta} com os filtros: {filtros}")
    try:
        observador.start()
        while True:
            time.sleep(5)  # Mantém o script rodando
    except KeyboardInterrupt:
        print("\nEncerrando vigilância...")
        observador.stop()
    observador.join()

def minha_acao(caminho_arquivo: str):
    print("--------------------------------------------\nCOMEÇANDO EXECUTE\n")
    print(f"Processando o arquivo: {caminho_arquivo}")
    try:
        execute(caminho_arquivo)  # Agora a função execute recebe o arquivo a ser processado
    except Exception as e:
        print(f"Erro ao processar o arquivo {caminho_arquivo}: {e}")
    print("\nFIM EXECUTE\n---------------------------------------------------")

def execute(caminho_arquivo: str):
    # Pequena espera para garantir que o arquivo foi totalmente gravado
    time.sleep(5)
    
    nome_arquivo = Path(caminho_arquivo).name
    arquivos_processados = bd.carregar_log()

    if nome_arquivo in arquivos_processados:
        print(f"📌 Arquivo {nome_arquivo} já foi processado. Pulando...")
        return

    # Aqui assumimos que o nome do arquivo segue o padrão esperado: algo como "xxx ddmm.xlsx"
    try:
        numero = nome_arquivo.split()[-1][:4]
        mes = int(numero[2:])  # Assume que os dois últimos dígitos são o mês
        dia = int(numero[:2])
    except Exception as e:
        raise ValueError(f"Padrão do nome do arquivo inválido ({nome_arquivo}): {e}")
    
    data_formatada: pd.Timestamp = pd.Timestamp(year=2025, month=mes, day=dia)
    print(f"Data FORMATADA: {data_formatada}")
    print(f"Data VALUE: {data_formatada.value}")
    
    # Processamento dos dados utilizando o arquivo específico
    df_safra = es.execute(data_formatada.strftime("%d-%m-%Y"), Path(caminho_arquivo))
    df_anita = ra.execute(data_formatada.strftime("%Y-%m-%d"))
    
    print("Processando...\n")
    conciliado = conciliacao_DDA(df_safra, df_anita)
    print(f"Tabela Final\n{conciliado}")

    nome_arquivo_saida = f"relatorio_{data_formatada.strftime('%d-%m-%Y')}.xlsx"
    caminho_saida = Path(f"\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025\\RelatórioDDA\\{nome_arquivo_saida}")

    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
        df_safra.to_excel(writer, sheet_name="Safra", index=False)
        df_anita.to_excel(writer, sheet_name="Anita", index=False)
        conciliado.to_excel(writer, sheet_name="Conciliado", index=False)
    
    bd.salvar_no_log(nome_arquivo)
    print("Concluido! ;)")

if __name__ == "__main__":
    if not bd.banco_existe():
        bd.criar_tabela()
    pasta_para_vigiar = Path("\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025")
    print(pyfiglet.figlet_format("DDA\nAutomatizado\n", font="slant"))
    print(f"Lista de arquivos processados:\n{bd.carregar_log()}")
    extensoes = [".xlsx"]
    vigiar_pasta(pasta_para_vigiar, extensoes)
