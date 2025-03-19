import psycopg2

from core.config import db_config as config

def db_conn():
    conn = psycopg2.connect(
            host = config.host,
            database = config.name,
            user = config.user,
            password = config.password,
            )
    conn.autocommit = True
    return conn

def execute_command(command:str, args:tuple | list = None) -> list | None:
    with db_conn() as conn:
        with conn.cursor() as cur:
            try:
                if args:
                    cur.execute(command, args)
                else: cur.execute(command)

                if cur.description: return cur.fetchall()
            except psycopg2.errors.Error:
                return None
            
def fetch_entry(table:str, targets:str, fields:str = None, ids:tuple = None) -> tuple:
    if fields is not None and ids is not None:
        cmd = execute_command(f"SELECT {targets} FROM {table} "
                              f"WHERE {fields} = {('%s,' * len(ids)).removesuffix(',')};", ids)
    else:
        cmd = execute_command(f"SELECT {targets} FROM {table};")
    return cmd

def insert_entry(table:str, fields:str, vars:tuple):
    execute_command(f"INSERT INTO {table}({fields}) "
                    f"VALUES({('%s,' * len(vars)).removesuffix(',')});", vars)
    
def delete_entry(table:str, fields:str, ids:tuple):
    execute_command(f"DELETE FROM {table} "
                    f"WHERE {fields} = {('%s,' * len(ids)).removesuffix(',')};", ids)
