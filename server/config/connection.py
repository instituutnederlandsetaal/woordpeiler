import os

from dotenv import load_dotenv

load_dotenv()


def get_reader_conn_str():
    return f"""
    user={os.getenv('READER_USER', 'reader')}
    password={os.getenv('READER_PASSWORD', 'reader')}
    {get_conn_str()}
    """


def get_writer_conn_str():
    return f"""
    user={os.getenv('POSTGRES_USER', 'writer')}
    password={os.getenv('POSTGRES_PASSWORD', 'writer')}
    {get_conn_str()}
    """


def get_conn_str():
    return f"""
    dbname={os.getenv('POSTGRES_DB', 'woordwacht')}
    host={os.getenv('POSTGRES_HOST', 'localhost')}
    port={os.getenv('POSTGRES_PORT', '5432')}
    """
