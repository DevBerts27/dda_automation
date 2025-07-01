import sqlite3
from pathlib import Path

# Nome do banco de dados
DB_PATH = "LOG.db"

def criar_tabela():
    """Cria a tabela no banco de dados, se não existir."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_arquivo TEXT UNIQUE NOT NULL,
                data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def carregar_log() -> set:
    """Consulta o banco de dados para obter os arquivos já processados."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome_arquivo FROM execucoes")
        return {row[0] for row in cursor.fetchall()}

def salvar_no_log(arquivo: str) -> None:
    """Registra um arquivo no banco de dados após processamento."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO execucoes (nome_arquivo) VALUES (?)", (arquivo,))
        conn.commit()
        
def banco_existe() -> bool:
    """Verifica se o banco de dados e a tabela existem."""
    if not Path(DB_PATH).exists():
        return False
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM execucoes LIMIT 1;")  # Verifica se a tabela existe
        return True
    except sqlite3.OperationalError:
        return False