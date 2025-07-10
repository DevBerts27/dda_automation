import os
import time
from pathlib import Path
from typing import List

import pandas as pd
import pyfiglet
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import numpy as np

import Database.BD_cache as bd
import extrato_safra as es
import relat_anita as ra
import relat_adv as radv

import datetime as dt

NOME_TABELA_BANCO = "execucoes"

def _conciliacao_DDA(rel_safra: pd.DataFrame, rel_anita: pd.DataFrame):

    rel_anita["SALDO"] = (
        rel_anita["SALDO"].replace(",", ".", regex=True).astype(float).round(2)
    ).sort_values(ascending=False)

    rel_safra["Valor_novo"] = np.where(
        (rel_safra["Nominal (R$)"] > rel_safra["Valor Total (R$)"])
        & (rel_safra["Valor Total (R$)"] != 0),
        rel_safra["Valor Total (R$)"],
        rel_safra["Nominal (R$)"],
    )

    conciliado = rel_safra.merge(
        rel_anita,
        left_on="Valor_novo",
        right_on="SALDO",
        how="outer",
    )

    nota_map = rel_anita.set_index("SALDO")["NOTA"].to_dict()
    conciliado["nota_anita"] = conciliado["SALDO"].map(nota_map)

    # duplicata = rel_anita.set_index("SALDO")["DUPLICATA"].to_dict()
    # conciliado["duplicata_anita"] = conciliado["SALDO"].map(duplicata)

    cod_for = rel_anita.set_index("SALDO")["COD_FORNECEDOR"].to_dict()
    conciliado["cod_fornecedor_anita"] = conciliado["SALDO"].map(cod_for)

    nome_for = rel_anita.set_index("SALDO")["NOME_FORNECEDOR"].to_dict()
    conciliado["nome_fornecedor_anita"] = conciliado["SALDO"].map(nome_for)

    transportadora = rel_anita.set_index("SALDO")["TRANSPORTADORA"].to_dict()
    conciliado["cod_transportadora_anita"] = conciliado["SALDO"].map(transportadora)

    n_documento = rel_safra.set_index("Valor_novo")["Nº documento"].to_dict()
    conciliado["n_documento_safra"] = conciliado["Valor_novo"].map(n_documento)

    situacao = rel_safra.set_index("Valor_novo")["Situação"].to_dict()
    conciliado["situacao_safra"] = conciliado["Valor_novo"].map(situacao)

    nome_ben = rel_safra.set_index("Valor_novo")["Beneficiário"].to_dict()
    conciliado["nome_beneficiario_safra"] = conciliado["Valor_novo"].map(nome_ben)

    # conciliado["nota_anita"] = conciliado["nota_anita"].drop_duplicates() # possível solução para o erro de duplicação de notas

    conciliado = conciliado.reindex(
        columns=[
            "Valor_novo",
            "nome_beneficiario_safra",
            "n_documento_safra",
            "situacao_safra",
            "SALDO",
            "nota_anita",
            "cod_transportadora_anita",
            "cod_fornecedor_anita",
            "nome_fornecedor_anita",
        ]
    ).sort_index(ascending=False)

    conciliado.rename(
        columns={"Valor_novo": "Valor_Safra", "SALDO": "Valor_Anita"}, inplace=True
    )

    conciliado["Conciliado"] = [
        f"=IF(A{i}=E{i},TRUE,FALSE)" for i in range(2, len(conciliado) + 2)
    ]
    
    conciliado["observacoes"] = None
    
    conciliado["para_maristela"] = None
    conciliado["para_loja"] = None
    
    return conciliado

def processar_arquivo(caminho_arquivo: Path):
    # Pequena espera para garantir que o arquivo foi totalmente gravado
    time.sleep(5)

    nome_arquivo = caminho_arquivo.name
    arquivos_processados = bd.carregar_log(NOME_TABELA_BANCO)

    if nome_arquivo in arquivos_processados:
        print(f"📌 Arquivo {nome_arquivo} já foi processado. Pulando...")
        return

    try:
        # Exemplo: o nome do arquivo deve terminar com "DDMM" antes da extensão
        numero = nome_arquivo.split()[-1][:4]
        dia = int(numero[:2])
        mes = int(numero[2:])
    except Exception as e:
        raise ValueError(f"Padrão do nome do arquivo inválido ({nome_arquivo}): {e}")

    data_formatada: pd.Timestamp = pd.Timestamp(
        year=dt.datetime.now().year, month=mes, day=dia
    )
    print(f"Data FORMATADA: {data_formatada}")
    print(f"Data VALUE: {data_formatada.value}")

    # Processamento dos dados
    df_safra = es.execute(data_formatada.strftime("%d-%m-%Y"), caminho_arquivo)
    df_anita = ra.execute(data_formatada.strftime("%Y-%m-%d"))
    df_adv = radv.execute(data_formatada.strftime("%Y-%m-%d"))

    print("Processando...\n")
    conciliado = _conciliacao_DDA(df_safra, df_anita)
    print(f"Tabela Final\n{conciliado}")

    nome_arquivo_saida = f"relatorio_{data_formatada.strftime('%d-%m-%Y')}.xlsx"
    caminho_saida = Path(
        f"\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025\\RelatórioDDA\\{nome_arquivo_saida}"
    )

    # Para teste local, descomente:
    # caminho_saida = Path(
    #     f"C:\\Users\\pedro.bertoldo\\Desktop\\asdasd\\{nome_arquivo_saida}"
    # )

    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
        df_safra.to_excel(writer, sheet_name="Safra", index=False)
        df_anita.to_excel(writer, sheet_name="Anita", index=False)
        df_adv.to_excel(writer, sheet_name="ADV", index=False)
        conciliado.to_excel(writer, sheet_name="Conciliado", index=False)

    bd.salvar_no_log(nome_arquivo,NOME_TABELA_BANCO)
    print("Concluído! ;)")


def main_loop(caminho_pasta: Path, extensoes: List[str]):
    print("Iniciando loop de verificação (a cada 60 segundos)...")
    while True:
        try:
            arquivos_processados = bd.carregar_log(NOME_TABELA_BANCO)
            # Listar os arquivos com as extensões desejadas
            arquivos = [
                arquivo
                for arquivo in caminho_pasta.iterdir()
                if arquivo.suffix in extensoes and arquivo.is_file()
            ]
            # Filtrar apenas os arquivos que ainda não foram processados
            novos = [
                arquivo
                for arquivo in arquivos
                if arquivo.name not in arquivos_processados
            ]

            if novos:
                print(f"{len(novos)} novo(s) arquivo(s) encontrado(s).")
                for arquivo in novos:
                    try:
                        print(f"Processando arquivo: {arquivo.name}")
                        processar_arquivo(arquivo)
                    except Exception as e:
                        print(f"Erro ao processar {arquivo.name}: {e}")
            else:
                print("Nenhum novo arquivo encontrado.")
        except Exception as e:
            print(f"Erro no loop principal: {e}")

        time.sleep(60)


if __name__ == "__main__":
    if not bd.banco_existe(NOME_TABELA_BANCO):
        bd.criar_tabela(NOME_TABELA_BANCO)

    print(pyfiglet.figlet_format("DDA\nAutomatizado\n", font="slant"))
    print(f"Lista de arquivos processados:\n{bd.carregar_log(NOME_TABELA_BANCO)}")

    # Defina a pasta que será verificada DOCKER
    # pasta_para_verificar = Path(
    #     "\\mnt\\m:\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\2025"
    # )

    ano = dt.datetime.today().year

    pasta_para_verificar = Path(
        f"\\\\portaarquivos\\Agenda\\TESOURARIA\\CONTAS A PAGAR\\Conciliação DDA\\{ano}"
    )

    # Para testes locais, descomente:
    # pasta_para_verificar = Path("C:\\Users\\pedro.bertoldo\\Desktop\\Pasta_teste")

    extensoes = [".xlsx"]
    main_loop(pasta_para_verificar, extensoes)
