import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("POSTGRES_HOST")
print(f"Connecting to {host}.")


def get_reader_conn_str():
    return f"""
    user={os.getenv('READER_USER')}
    password={os.getenv('READER_PASSWORD')}
    {get_conn_str()}
    """


def get_writer_conn_str():
    return f"""
    user={os.getenv('POSTGRES_USER')}
    password={os.getenv('POSTGRES_PASSWORD')}
    {get_conn_str()}
    """


def get_conn_str():
    return f"""
    dbname={os.getenv('POSTGRES_DB')}
    host={host}
    port={os.getenv('DATABUILDER_PORT')}
    """
