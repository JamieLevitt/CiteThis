# from google.cloud.sql.connector import Connector
# import pg8000
# from sqlalchemy.engine import create_engine, Engine
# import sqlalchemy
import psycopg2

from core.config import db_config as config

# __connector = Connector()

# def __get_engine() -> Engine:
#     return create_engine(
#         "postgresql+pg8000://",
#         creator=lambda: __connector.connect(
#             config.conn, "pg8000",
#             user = config.user,
#             password = config.password,
#             db = config.name
#         ),
#         isolation_level = "AUTOCOMMIT",  #Enables autocommit mode
#     )

# engine : Engine = None

# def init_db_engine():
#     globals()["engine"] = __get_engine()

def db_conn():
    conn = psycopg2.connect(
            host = config.host,
            database = config.name,
            user = config.user,
            password = config.password,
            )
    conn.autocommit = True
    return conn

#psql -h 35.244.83.45 -U postgres -d postgres 
#K36A8`*GLQy>i)gp

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
    # if engine:
    #     with engine.connect() as conn:
    #         try:
    #             stmt = sqlalchemy.text(command)
    #             if args:
    #                 result = conn.execute(stmt, args)
    #             else:
    #                 result = conn.execute(stmt)
    #             if result.returns_rows:
    #                 return result.fetchall()
    #         except Exception:
    #             return []
    # else:
    #     init_db_engine()
    #     return execute_command(command, args)
        
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
