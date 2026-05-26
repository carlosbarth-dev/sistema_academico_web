import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
    "dbname": os.getenv("PGDATABASE", "sistema_academico_web"),
}


def _config_sem_banco():
    """Eu uso essa conexao temporaria para criar o banco caso ele ainda nao exista."""

    config = DB_CONFIG.copy()
    config["dbname"] = "postgres"
    return config


def criar_banco_se_necessario():
    """
    Eu deixei o proprio sistema criar o banco se ele nao existir.

    No pgAdmin4 o banco tambem pode ser criado manualmente, mas assim o projeto
    fica mais facil de testar em outro computador.
    """

    nome_banco = DB_CONFIG["dbname"]
    conexao = psycopg2.connect(**_config_sem_banco())
    conexao.autocommit = True

    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nome_banco,))
            existe = cursor.fetchone()

            if not existe:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nome_banco))
                )
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
        with conexao.cursor() as cursor:
            cursor.execute(comandos_sql)


@contextmanager
def get_connection():
    """
    Essa funcao entrega uma conexao pronta e fecha tudo no final.

    Anotacao minha:
    Eu uso contextmanager para evitar esquecer commit, rollback ou close.
    Isso deixa o sistema mais organizado e parecido com um padrao profissional.
    """

    conexao = psycopg2.connect(**DB_CONFIG)

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
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()


def fetch_one(query, params=None):
    with get_connection() as conexao:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()


def execute(query, params=None):
    with get_connection() as conexao:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())

            if cursor.description:
                return cursor.fetchone()

            return None
