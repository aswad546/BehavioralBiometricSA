# worker/db_utils.py
import os
import psycopg2
from psycopg2 import sql, pool
from contextlib import contextmanager
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=20,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    if connection_pool:
        print("Worker: Connection pool created successfully")
except Exception as e:
    print("Worker: Error creating connection pool:", e)
    connection_pool = None

def get_db_connection():
    if connection_pool:
        try:
            return connection_pool.getconn()
        except Exception as e:
            print("Worker: Error getting connection from pool:", e)
            raise
    else:
        raise Exception("Worker: Connection pool not initialized")

def release_db_connection(conn):
    if connection_pool:
        connection_pool.putconn(conn)

@contextmanager
def get_db_connection_context():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        release_db_connection(conn)

def insert_into_table(table_name, data):
    columns = data.keys()
    values = []
    for column in columns:
        value = data[column]
        if isinstance(value, list) and not value:
            values.append(None)
        elif isinstance(value, (list, dict)):
            import json
            values.append(json.dumps(value))
        else:
            values.append(value)
    insert_statement = sql.SQL('INSERT INTO {table} ({fields}) VALUES ({values})').format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        values=sql.SQL(', ').join(sql.Placeholder() * len(columns))
    )
    return insert_statement, values
