import os
from pathlib import Path
from typing import List
import time

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
        """
        Construtor para o manipulador de eventos.

        :param filtros: Lista de extensões (ex: ['.txt', '.csv']) que o script deve monitorar.
        :param acao: Função a ser executada quando um arquivo novo correspondente aos filtros for detectado.
        """
        self.filtros = filtros
        self.acao = acao

    def on_created(self, event):
        """
        Método chamado quando um novo arquivo é criado na pasta monitorada.
        """
        if not event.is_directory:
            _, extensao = os.path.splitext(event.src_path)
            if extensao in self.filtros:
                print(f"Novo arquivo detectado: {event.src_path}")
                self.acao(event.src_path)

def conciliacao_DDA(rel_safra: pd.DataFrame, rel_anita: pd.DataFrame):

    rel_safra["Nominal (R$)"] = (
        rel_safra["Nominal (R$)"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)
    rel_anita["SALDO"] = (
        rel_anita["SALDO"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)
    
    conciliado = rel_safra.merge(rel_anita, left_on="Nominal (R$)", right_on="SALDO", how="outer")

    conciliado = conciliado.reindex(columns=['Nominal (R$)','SALDO']).sort_index(ascending=False)
    # conciliado['Diferença'] = (conciliado['Nominal (R$)'] - conciliado['SALDO']).round(2)
    # conciliado["Conciliado"] = conciliado["Diferença"] == 0
    conciliado["Conciliado"] = [f"=IF(A{i}=B{i},TRUE,FALSE)" for i in range(2, len(conciliado) + 2)]

    return conciliado

def vigiar_pasta(caminho_pasta: str, filtros: List[str]):
    """
    Função principal para vigiar uma pasta e executar uma ação ao detectar novos arquivos.

    :param caminho_pasta: Caminho da pasta a ser monitorada.
    :param filtros: Lista de extensões de arquivo a serem monitoradas.
    """
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
    """
    Função que será executada sempre que um novo arquivo for detectado.

    :param caminho_arquivo: Caminho completo do arquivo detectado.
    """
    print("--------------------------------------------\nCOMEÇANDO EXECUTE\n")
    print(f"Processando o arquivo: {caminho_arquivo}")
    
    execute()
    
    print("\nFIM EXECUTE\n---------------------------------------------------")

    print(f"Esperando arquivo...")
    
def execute():
    
    time.sleep(5)
    
    arquivos_processados = bd.carregar_log()

    for arquivo in es.encontra_arquivos():
        if arquivo.name in arquivos_processados:
            print(f"📌 Arquivo {arquivo.name} já foi processado. Pulando...")
            continue  # Em vez de "break", usamos "continue" para ignorar apenas este arquivo e seguir para o próximo

        nome_arquivo = arquivo.name
        numero = nome_arquivo.split()[-1][:4]
        print(f"Numero: {numero}")
        mes = int(numero[2:])  # Primeiro dois dígitos para o mês
        dia = int(numero[:2])
        data_formatada:pd.Timestamp = pd.Timestamp(year=2025, month=mes, day=dia)

        print(f"Data FORMATADA: {data_formatada}\n")
        print(f"Data VALUE: {data_formatada.value}\n")
        
        df_safra = es.execute(
            data_formatada.strftime("%d-%m-%Y"),arquivo
        )  # Busca em padrão brasileiro de datas
        df_anita = ra.execute(
            data_formatada.strftime("%Y-%m-%d")
        )  # Busca em padrão Americano de datas

        print("Processando...\n")
        conciliado = conciliacao_DDA(df_safra, df_anita)

        print(f"Tabela Final\n{conciliado}")

        nome_arquivo = f"relatorio_{data_formatada.strftime('%d-%m-%Y')}.xlsx"
        
        caminho_saida = Path(f"\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025\\RelatórioDDA\\{nome_arquivo}")
        #caminho_saida = Path(f"C:\\Users\\pedro.bertoldo\\Desktop\\Pasta_teste_2\\{nome_arquivo}")

        with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
            df_safra.to_excel(writer, sheet_name="Safra", index=False)
            df_anita.to_excel(writer, sheet_name="Anita", index=False)
            conciliado.to_excel(writer, sheet_name="Conciliado", index=False)
        
        bd.salvar_no_log(arquivo.name)
        print("Concluido! ;)\n")

if __name__ == "__main__":
    if not bd.banco_existe():
        bd.criar_tabela()
    pasta_para_vigiar = Path("\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025")
    #pasta_para_vigiar = Path("C:\\Users\\pedro.bertoldo\\Desktop\\Pasta_teste")
    print(pyfiglet.figlet_format("DDA\nAutomatizado\n", font="slant"))
    print(f"Lista de arquivos processados:\n{bd.carregar_log()}")
    # print("\nLista de Extratos encontrados do Safra...\n")
    # [print(f">> {arquivo.name}") for arquivo in es.encontra_arquivos() ]
    extensoes = [".xlsx"]
    vigiar_pasta(pasta_para_vigiar, extensoes)
    