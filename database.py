import os
import re
from contextlib import contextmanager
from pathlib import Path

import pg8000.dbapi
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
    "database": os.getenv("PGDATABASE", "sistema_academico_web"),
}


def _config_sem_banco():
    """Eu uso essa conexao temporaria para criar o banco caso ele ainda nao exista."""

    config = DB_CONFIG.copy()
    config["database"] = "postgres"
    return config


def _validar_nome_banco(nome_banco):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome_banco):
        raise ValueError("Nome de banco invalido. Use apenas letras, numeros e underline.")


def criar_banco_se_necessario():
    """
    Eu deixei o proprio sistema criar o banco se ele nao existir.

    No pgAdmin4 o banco tambem pode ser criado manualmente, mas assim o projeto
    fica mais facil de testar em outro computador.
    """

    nome_banco = DB_CONFIG["database"]
    _validar_nome_banco(nome_banco)

    conexao = pg8000.dbapi.connect(**_config_sem_banco())
    conexao.autocommit = True

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nome_banco,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute(f'CREATE DATABASE "{nome_banco}"')
        cursor.close()
    finally:
        conexao.close()


def inicializar_banco():
    """
    Eu centralizei a criacao das tabelas aqui.

    O arquivo schema.sql fica separado para eu conseguir abrir no pgAdmin4,
    estudar as tabelas e entender melhor a modelagem do banco.
    """

    criar_banco_se_necessario()

    caminho_schema = Path(__file__).with_name("schema.sql")

    with open(caminho_schema, "r", encoding="utf-8") as arquivo:
        comandos_sql = arquivo.read()

    with get_connection() as conexao:
        cursor = conexao.cursor()
        cursor.execute(comandos_sql)
        cursor.close()


@contextmanager
def get_connection():
    """
    Essa funcao entrega uma conexao pronta e fecha tudo no final.

    Anotacao minha:
    Eu uso contextmanager para evitar esquecer commit, rollback ou close.
    Isso deixa o sistema mais organizado e parecido com um padrao profissional.
    """

    conexao = pg8000.dbapi.connect(**DB_CONFIG)

    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def fetch_all(query, params=None):
    with get_connection() as conexao:
        cursor = conexao.cursor()
        cursor.execute(query, params or ())
        colunas = [coluna[0] for coluna in cursor.description]
        linhas = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        cursor.close()
        return linhas


def fetch_one(query, params=None):
    with get_connection() as conexao:
        cursor = conexao.cursor()
        cursor.execute(query, params or ())
        linha = cursor.fetchone()

        if not linha:
            cursor.close()
            return None

        colunas = [coluna[0] for coluna in cursor.description]
        resultado = dict(zip(colunas, linha))
        cursor.close()
        return resultado


def execute(query, params=None):
    with get_connection() as conexao:
        cursor = conexao.cursor()
        cursor.execute(query, params or ())

        if cursor.description:
            linha = cursor.fetchone()
            colunas = [coluna[0] for coluna in cursor.description]
            resultado = dict(zip(colunas, linha))
            cursor.close()
            return resultado

        cursor.close()
        return None
