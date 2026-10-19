import sqlite3
from pathlib import Path

PASTA = Path(__file__).parent
CAMINHO_BANCO = PASTA / "streaming.db"
CAMINHO_SCHEMA = PASTA / "schema.sql"


def obter_conexao(caminho: Path = CAMINHO_BANCO) -> sqlite3.Connection:
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco(caminho: Path = CAMINHO_BANCO) -> None:
    with obter_conexao(caminho) as conexao:
        conexao.executescript(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
