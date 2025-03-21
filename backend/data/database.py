import psycopg2
from core.config import db_config as config

def db_conn() -> psycopg2.extensions.connection:
    """
    Establishes and returns a connection to the PostgreSQL database.
    The connection is set to autocommit mode to apply changes immediately.
    """
    conn = psycopg2.connect(
        host=config.host,
        database=config.name,
        user=config.user,
        password=config.password,
    )
    conn.autocommit = True  # Ensures changes are committed without explicit commit commands
    return conn

def execute_command(command: str, args: tuple | list = None) -> list | None:
    """
    Executes an SQL command on the database.
    
    Args:
        command (str): The SQL command to execute.
        args (tuple | list, optional): Parameters to safely insert into the SQL command.
    
    Returns:
        list | None: Fetched results if applicable, otherwise None.
    """
    with db_conn() as conn:
        with conn.cursor() as cur:
            try:
                if args:
                    cur.execute(command, args)  # Executes command with parameters
                else:
                    cur.execute(command)  # Executes command without parameters
                
                if cur.description:  # If there is a result set, fetch it
                    return cur.fetchall()
            except psycopg2.errors.Error:
                return None  # Returns None if an error occurs during execution

def fetch_entry(table: str, targets: str, fields: str = None, ids: tuple = None) -> tuple | None:
    """
    Retrieves data from a specified table based on given criteria.
    
    Args:
        table (str): The table name to fetch data from.
        targets (str): The columns to retrieve.
        fields (str, optional): The condition column(s) for filtering.
        ids (tuple, optional): The values corresponding to the fields.
    
    Returns:
        tuple | None: Retrieved database records or None if query fails.
    """
    if fields is not None and ids is not None:
        cmd = execute_command(f"SELECT {targets} FROM {table} "
                              f"WHERE {fields} = {('%s,' * len(ids)).removesuffix(',')};", ids)
    else:
        cmd = execute_command(f"SELECT {targets} FROM {table};")
    return cmd

def insert_entry(table: str, fields: str, vars: tuple) -> None:
    """
    Inserts a new record into the specified table.
    
    Args:
        table (str): The table name.
        fields (str): The column names where values will be inserted.
        vars (tuple): The values to insert.
    """
    execute_command(f"INSERT INTO {table}({fields}) "
                    f"VALUES({('%s,' * len(vars)).removesuffix(',')});", vars)

def delete_entry(table: str, fields: str, ids: tuple) -> None:
    """
    Deletes records from a specified table based on given conditions.
    
    Args:
        table (str): The table name.
        fields (str): The condition column(s) for identifying rows to delete.
        ids (tuple): The values corresponding to the fields.
    """
    execute_command(f"DELETE FROM {table} "
                    f"WHERE {fields} = {('%s,' * len(ids)).removesuffix(',')};", ids)
