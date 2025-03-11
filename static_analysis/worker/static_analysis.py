# static_analysis.py
import time
import gc
import traceback
from multiprocessing import Manager
import psycopg2
import multiprocessing

from config import BEHAVIORAL_SOURCES, DB_WRITE_MODE
from db_utils import insert_into_table, get_db_connection_context
# from queue_utils import push_to_queue
from utils import (
    split_APIs,
    check_behavioral_source,
    filter_sources,
    filter_sinks,
    write_code_to_file,
    find_max_aggregation_score,
    find_event_listeners_attached,
    get_all_source_APIs,
    find_max_behavioral_score,
    find_max_fp_score,
    calculate_access_count,
)

def get_submission_url(submission_id):
    """Retrieve the submission URL from the submissions table given submission_id."""
    try:
        with get_db_connection_context() as conn:
            cur = conn.cursor()
            cur.execute("SELECT url FROM submissions WHERE id = %s;", (submission_id,))
            result = cur.fetchone()
            cur.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        print("Error fetching submission URL:", e)
        return None

# Assume these functions are imported from your static_helpers module.
from dfg_construct.static_helpers import get_data_flow, search_API, find_dataflow

def generate_graph_with_timeout(filename, url, lock, timeout=450):
    """
    Run get_data_flow directly in the main thread.
    The internal Timeout context (using signal.alarm) inside get_data_flow
    will enforce the timeout.
    """
    # Optionally, you could set a timeout in this wrapper using signal.alarm here,
    # but since get_data_flow already uses a Timeout context, we simply call it.
    return get_data_flow(filename, url, lock, benchmarks={})



class StaticAnalyzer:
    def __init__(self, lock):
        self.lock = lock

    def analyze_script(self, id, url, code, APIs, submission_id):
        # Skip unwanted sources.
        if ("chrome-extension://pogpcelnjdlchjbjcakalbgppnhkondb" in url or 
            "devtools://devtools" in url):
            return

        insertion_data = {
            'script_id': id,
            'script_url': url,
            'code': code,
            'max_api_aggregation_score': -1,
            'behavioral_api_agg_count': -1,
            'fp_api_agg_count': -1,
            'max_aggregated_apis': [],
            'max_behavioral_api_aggregation_score': -1,
            'aggregated_behavioral_apis': [],
            'max_fingerprinting_api_aggregation_score': -1,
            'aggregated_fingerprinting_apis': [],
            'attached_listeners': [],
            'fingerprinting_source_apis': [],
            'behavioral_source_apis': [],
            'behavioral_source_api_count': 0,
            'fingerprinting_source_api_count': 0,
            'behavioral_apis_access_count': {},
            'fingerprinting_api_access_count': {},
            'graph_construction_failure': False,
            'dataflow_to_sink': False,
            'apis_going_to_sink': {},
            'submission_url': None
        }

        print("Processing script:", id)
        APIs, unique_APIs = split_APIs(APIs)
        print(len(APIs), len(unique_APIs))
        if check_behavioral_source(unique_APIs):
            print('Has behavioral sources')
            filename = f"/tmp/exp{id}.js"
            write_code_to_file(code, filename)
            source_APIs = filter_sources(APIs)
            sink_APIs = filter_sinks(APIs)
            (insertion_data['behavioral_apis_access_count'],
             insertion_data['fingerprinting_api_access_count']) = calculate_access_count(APIs)
            insertion_data['attached_listeners'] = find_event_listeners_attached(APIs)
            behavioral_src, fp_src = get_all_source_APIs(source_APIs)
            insertion_data['behavioral_source_apis'] = behavioral_src
            insertion_data['fingerprinting_source_apis'] = fp_src
            insertion_data['behavioral_source_api_count'] = len(behavioral_src)
            insertion_data['fingerprinting_source_api_count'] = len(fp_src)
            print('Generating graph')
            start_time = time.time()
            # pdg = generate_graph_with_timeout(filename, url, self.lock, timeout=450) if url.includes('googletagmanager.com') != True else None
            pdg = generate_graph_with_timeout(filename, url, self.lock, timeout=450)
            elapsed_time = time.time() - start_time
            print(f"Took: {elapsed_time:.2f} seconds for graph generation")
            insertion_data['submission_url'] =  get_submission_url(submission_id)
            if pdg is None:
                print("Unable to generate graph for url:", url)
                insertion_data['graph_construction_failure'] = True
                self._finalize_result(insertion_data)
                return

            if not sink_APIs:
                print("File does not call any of the known sinks")
            sink_node_apis = {}
            for api in sink_APIs:
                sink_nodes = []
                snippet = (code[api['offset']: api['offset']+30] 
                           if len(code) > api['offset'] + 30 
                           else code[api['offset']:])
                search_API(pdg, api['offset'], snippet, api['API'].split('.')[1], sink_nodes)
                if sink_nodes and sink_nodes[0].get_id() not in sink_node_apis:
                    sink_node_apis[sink_nodes[0].get_id()] = api['API']
            endpoint_score = {}
            for api in source_APIs:
                source_api = []
                dataflow = []
                if len(api['API'].split('.')) < 2:
                    continue
                snippet = (code[api['offset']: api['offset']+30]
                           if len(code) > api['offset'] + 30 
                           else code[api['offset']:])
                search_API(pdg, api['offset'], snippet, api['API'].split('.')[1], source_api)
                if source_api:
                    endpoints = []
                    statement = source_api[0]
                    endpoints += find_dataflow(statement, dataflow)
                    old_endpoints = endpoints.copy()
                    endpoints += dataflow
                    for end in set(endpoints):
                        eid = end.get_id()
                        if eid not in endpoint_score:
                            endpoint_score[eid] = {
                                'source_count': 1,
                                'behavioral_count': 0,
                                'behavioral_apis': [],
                                'fp_count': 0,
                                'fp_apis': [],
                                'source_apis': [api['API']],
                                'end': True if end in old_endpoints else False
                            }
                            if api['API'] in BEHAVIORAL_SOURCES:
                                endpoint_score[eid]['behavioral_count'] += 1
                                endpoint_score[eid]['behavioral_apis'].append(api['API'])
                            else:
                                endpoint_score[eid]['fp_count'] += 1
                                endpoint_score[eid]['fp_apis'].append(api['API'])
                        else:
                            if api['API'] not in endpoint_score[eid]['source_apis']:
                                if api['API'] in BEHAVIORAL_SOURCES:
                                    endpoint_score[eid]['behavioral_count'] += 1
                                    endpoint_score[eid]['behavioral_apis'].append(api['API'])
                                else:
                                    endpoint_score[eid]['fp_count'] += 1
                                    endpoint_score[eid]['fp_apis'].append(api['API'])
                                endpoint_score[eid]['source_apis'].append(api['API'])
                                endpoint_score[eid]['source_count'] += 1

            max_agg, max_aggregated, beh_agg, fp_agg = find_max_aggregation_score(endpoint_score)
            insertion_data['max_api_aggregation_score'] = max_agg
            insertion_data['max_aggregated_apis'] = max_aggregated
            insertion_data['behavioral_api_agg_count'] = beh_agg
            insertion_data['fp_api_agg_count'] = fp_agg

            max_beh, aggregated_beh = find_max_behavioral_score(endpoint_score)
            insertion_data['max_behavioral_api_aggregation_score'] = max_beh
            insertion_data['aggregated_behavioral_apis'] = aggregated_beh

            max_fp, aggregated_fp = find_max_fp_score(endpoint_score)
            insertion_data['max_fingerprinting_api_aggregation_score'] = max_fp
            insertion_data['aggregated_fingerprinting_apis'] = aggregated_fp

            sink_data = {}
            for key, value in endpoint_score.items():
                if key in sink_node_apis:
                    s_api = sink_node_apis[key]
                    if s_api in sink_data:
                        sink_data[s_api]['source_apis'] += value['source_apis']
                        sink_data[s_api]['source_apis'] = list(set(sink_data[s_api]['source_apis']))
                        sink_data[s_api]['source_count'] = len(sink_data[s_api]['source_apis'])
                    else:
                        sink_data[s_api] = value
            if sink_data:
                insertion_data['dataflow_to_sink'] = True
                insertion_data['apis_going_to_sink'] = sink_data
            else:
                print("No data flow to sinks")
            
            self._finalize_result(insertion_data)
        else:
            print("File with id", id, "contains no relevant sources")

    def _finalize_result(self, insertion_data: dict):
        # Prepare the insert statement.
        stmt, values = insert_into_table("multicore_static_info", insertion_data)
        if DB_WRITE_MODE.lower() == "immediate":
            # Immediate write to DB.
            try:
                with get_db_connection_context() as conn:
                    cur = conn.cursor()
                    cur.execute(stmt, values)
                    conn.commit()
                    cur.close()
                print("Results written immediately to the DB for script id")
            except Exception as e:
                print("Error writing result to DB immediately:", e)
        elif DB_WRITE_MODE.lower() == "batch":
            # # Batch mode: push the insert data into a Redis queue.
            # push_to_queue({"stmt": stmt.as_string(conn=get_db_connection_context().__enter__()),
            #                "values": values})
            print("Result pushed to Redis queue for later batch writing")
        else:
            print("Unknown DB_WRITE_MODE. No action taken.")

# (The worker and analyze() functions remain available if you need to process many scripts in parallel.)
def worker(data, lock):
    from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    id, url, code, APIs = data
    analyzer = StaticAnalyzer(lock)
    analyzer.analyze_script(id, url, code, APIs)
    cur.close()
    conn.close()

def analyze():
    from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    write_conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    write_cur = write_conn.cursor()
    print("Connected to the database.")
    with conn.cursor(name="custom_cursor") as cursor:
        cursor.itersize = 500
        create_table_query = '''
        DROP TABLE IF EXISTS multicore_static_info;
        CREATE TABLE IF NOT EXISTS multicore_static_info (
            script_id SERIAL,
            submission_url TEXT,
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
            apis_going_to_sink JSONB
        );
        '''
        write_cur.execute(create_table_query)
        write_conn.commit()
        print("Table 'multicore_static_info' created successfully.")

        query = "SELECT * FROM script_flow;"
        cursor.execute(query)
        import os
        num_workers = int(os.cpu_count() / 2)
        print(f"Number of available CPU cores: {num_workers}")
        from itertools import count
        counter = count()
        tasks = []
        while True:
            rows = cursor.fetchmany(500)
            if not rows:
                break
            tasks.extend([(id, url, code, APIs, next(counter)) for id, _, _, code, _, url, APIs, _ in rows])
            # Using ProcessPoolExecutor to process tasks in parallel.
            from concurrent.futures import ProcessPoolExecutor
            with Manager() as manager:
                lock = manager.Lock()
                with ProcessPoolExecutor(max_workers=num_workers) as executor:
                    futures = {executor.submit(worker, task, lock): task for task in tasks}
                    for future in futures:
                        try:
                            future.result()
                            print(f"Task completed successfully")
                        except Exception as exc:
                            print("Task generated an exception:", exc)
                            traceback.print_exc()
                            exit(1)
            tasks.clear()
            gc.collect()
        write_cur.close()
        write_conn.close()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Process multicore static info table and optionally export to CSV.")
    parser.add_argument('--export', help="Export multicore_static_info table to CSV at /tmp/<argument>", type=str, required=False)
    args = parser.parse_args()
    analyze()
    if args.export:
        from db_utils import export_table_to_csv
        export_table_to_csv(args.export)
