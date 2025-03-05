# api/db_utils.py
import os
import psycopg2
from psycopg2 import sql, pool
import pandas as pd
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
        print("API: Connection pool created successfully")
except Exception as e:
    print("API: Error creating connection pool:", e)
    connection_pool = None

def get_db_connection():
    if connection_pool:
        try:
            return connection_pool.getconn()
        except Exception as e:
            print("API: Error getting connection from pool:", e)
            raise
    else:
        raise Exception("API: Connection pool not initialized")

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

def export_table_to_csv(argument):
    with get_db_connection_context() as conn:
        try:
            query = "SELECT * FROM multicore_static_info;"
            df = pd.read_sql(query, conn)
            output_path = os.path.join("/vagrant/BehavioralBiometricSA/boya_results", argument, "multicore_static_info.csv")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            print(f"API: Exported multicore_static_info table to {output_path}")
            truncate_query = "TRUNCATE TABLE script_flow;"
            with conn.cursor() as cur:
                cur.execute(truncate_query)
                conn.commit()
            print("API: Truncated table script_flow.")
        except Exception as e:
            print("API: Error exporting table:", e)

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

def write_batch_to_database(batch):
    with get_db_connection_context() as conn:
        cur = conn.cursor()
        try:
            insert_statement = batch[0][0]
            values = [item[1] for item in batch]
            cur.executemany(insert_statement, values)
            conn.commit()
        except Exception as e:
            print("API: Error writing batch:", e)
        finally:
            cur.close()

def create_multicore_static_info_table(drop_table: bool):
    if drop_table:
        create_table_query = '''
        DROP TABLE IF EXISTS multicore_static_info;
        CREATE TABLE multicore_static_info (
            script_id SERIAL,
            script_url TEXT,
            code TEXT,
            max_api_aggregation_score FLOAT,
            behavioral_api_agg_count FLOAT,
            fp_api_agg_count FLOAT,
            max_aggregated_apis JSONB,
            max_behavioral_api_aggregation_score FLOAT,
            aggregated_behavioral_apis JSONB,
            max_fingerprinting_api_aggregation_score FLOAT,
            aggregated_fingerprinting_apis JSONB,
            attached_listeners JSONB,
            fingerprinting_source_apis JSONB,
            behavioral_source_apis JSONB,
            behavioral_source_api_count FLOAT,
            fingerprinting_source_api_count FLOAT,
            behavioral_apis_access_count JSONB,
            fingerprinting_api_access_count JSONB,
            graph_construction_failure BOOLEAN,
            dataflow_to_sink BOOLEAN,
            apis_going_to_sink JSONB,
            submission_url TEXT
        );
        '''
    else:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS multicore_static_info (
            script_id SERIAL,
            script_url TEXT,
            code TEXT,
            max_api_aggregation_score FLOAT,
            behavioral_api_agg_count FLOAT,
            fp_api_agg_count FLOAT,
            max_aggregated_apis JSONB,
            max_behavioral_api_aggregation_score FLOAT,
            aggregated_behavioral_apis JSONB,
            max_fingerprinting_api_aggregation_score FLOAT,
            aggregated_fingerprinting_apis JSONB,
            attached_listeners JSONB,
            fingerprinting_source_apis JSONB,
            behavioral_source_apis JSONB,
            behavioral_source_api_count FLOAT,
            fingerprinting_source_api_count FLOAT,
            behavioral_apis_access_count JSONB,
            fingerprinting_api_access_count JSONB,
            graph_construction_failure BOOLEAN,
            dataflow_to_sink BOOLEAN,
            apis_going_to_sink JSONB,
            submission_url TEXT
        );
        '''
    try:
        with get_db_connection_context() as conn:
            cur = conn.cursor()
            cur.execute(create_table_query)
            conn.commit()
            cur.close()
        print("API: Table multicore_static_info created successfully (drop_table={}).".format(drop_table))
    except Exception as e:
        print("API: Error creating multicore_static_info table:", e)
