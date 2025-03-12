import psycopg2
from psycopg2.errors import Error

from core.config import data_config as config

import sys

def db_conn():
    try:
        return psycopg2.connect(
            database = config.db_name,
            user = config.db_user,
            password = config.db_pass,
            host = config.db_host,
            port = config.db_port
            )
    except psycopg2.OperationalError as e:
        print("error")

#psql -h citethis-db.cbsiwywwk6pc.ap-southeast-2.rds.amazonaws.com -U administrator -d postgres 
#xEfhWGPDQltjeGoZJjuu

def execute_command(command:str, args:tuple | list = None):
    with db_conn() as conn:
        with conn.cursor() as cur:
            try:
                if args:
                    cur.execute(command, args)
                else: cur.execute(command)

                if cur.description: return cur.fetchall()

            except Error as e:
                return []
        
def fetch_entry(table:str, targets:str, fields:str = None, ids:tuple = None) -> tuple:
    if fields is not None:
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
