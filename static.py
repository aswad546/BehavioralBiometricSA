import psycopg2
from psycopg2 import sql
from static_helpers import *
import json
import os
import concurrent.futures
from itertools import count
import time
from multiprocessing import Manager
import argparse  # Added for command-line argument handling
import pandas as pd  # For exporting to CSV
import traceback


# Database connection parameters
host = 'localhost'  # Since it's running on the same device
port = '5434'  # The port the database listens on
dbname = 'vv8_backend'  # Database name
user = 'vv8'  # Username
password = 'vv8'  # Password
behavioral_sources = [
    'CompositionEvent', 
    'TouchEvent', 
    'PointerEvent', 
    'TextEvent', 
    'FocusEvent', 
    'MouseEvent', 
    'InputEvent', 
    'WheelEvent', 
    'DragEvent', 
    'KeyboardEvent',
    'Touch',
    'DeviceMotionEventAcceleration',
    'DeviceMotionEventRotationRate',
    'DeviceMotionEvent',
    'DeviceOrientationEvent'
    ]
####################################
browser_fingerprinting_sources = []
with open('/home/vagrant/BehavioralBiometricSA/fp_apis.txt', 'r') as file:
    browser_fingerprinting_sources = [line.strip() for line in file.readlines()]


known_sinks = [
    'Window.sessionStorage', 
    'MessagePort.postMessage', 
    'WebSocket.send', 
    'ServiceWorker.postMessage', 
    'Window.localStorage', 
    'Window.openDatabase', 
    'XMLHttpRequest.send', 
    'IDBObjectStore.put', 
    'RTCDataChannel.send', 
    'Client.postMessage', 
    'Window.postMessage', 
    'Window.indexedDB', 
    'Navigator.sendBeacon', 
    'DedicatedWorkerGlobalScope.postMessage', 
    'IDBObjectStore.add', 
    'Worker.postMessage', 
    'Document.cookie', 
    'HTMLInputElement.value', 
    'Node.textContent',
    'HTMLScriptElement.setAttribute',
    'HTMLScriptElement.src',
    'HTMLImageElement.src'
]

importantEvents = [
    'focus',
    'blur',
    'click',
    'copy',
    'paste',
    'dblclick',
    'devicemotion',
    'deviceorientation',
    'keydown',
    'keypress',
    'keyup',
    'mousedown',
    'mouseenter',
    'mouseleave',
    'mousemove',
    'mouseup',
    'orientationchange',
    'pointerdown',
    'pointermove',
    'scroll',
    'touchstart',
    'touchend',
    'touchmove',
    'wheel',
]

def export_table_to_csv(argument):
    """Export the `multicore_static_info` table to CSV and truncate the `script_flow` table."""
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    
    try:
        # Export `multicore_static_info` table
        query = "SELECT * FROM multicore_static_info;"
        df = pd.read_sql(query, conn)
        
        # Define the path to save the CSV for multicore_static_info
        output_path = f"/home/vagrant/BehavioralBiometricSA/company_analysis_results/{argument}/multicore_static_info.csv"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the DataFrame to CSV
        df.to_csv(output_path, index=False)
        print(f"Table `multicore_static_info` has been exported to {output_path}")
        
        # Export `script_flow` table
        query = "SELECT * FROM script_flow;"
        df = pd.read_sql(query, conn)
        
        # Define the path to save the CSV for script_flow
        output_path = f"/home/vagrant/BehavioralBiometricSA/company_analysis_results/{argument}/vv8_script_flow.csv"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the DataFrame to CSV
        df.to_csv(output_path, index=False)
        print(f"Table `script_flow` has been exported to {output_path}")
        
        # # Truncate the `script_flow` table
        # truncate_query = "TRUNCATE TABLE script_flow;"
        # with conn.cursor() as cur:
        #     cur.execute(truncate_query)
        #     conn.commit()
        # print("Table `script_flow` has been truncated.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        conn.close()


def duplicate_api(api, offset, APIs):
    for i in APIs:
        if i['API'] == api and i['offset'] == offset:
            return True
    return False


def split_APIs(APIs):
    apis = []
    only_apis = []
    for api in list(set(APIs)):
        construct = {}
        attr = ''
        offset = api.split(',')[0]
        only_api = api.split(',')[1]
        apiElements = only_api.split('.')
        if len(apiElements) > 2 and (apiElements[1] == 'addEventListener' or apiElements[1] == 'setAttribute') and len(apiElements) == 3:
            only_api = '.'.join(apiElements[:2])
            attr = apiElements[2]
        elif len(apiElements) == 2 and (apiElements[1] == 'addEventListener' or apiElements[1] == 'setAttribute'):
            continue
        # if duplicate_api(only_api, int(offset), apis) == True:
        construct['offset'] = int(offset)
        construct['API'] = only_api
        if attr != '':
            construct['attr'] = attr
        apis.append(construct)
        only_apis.append(construct['API'])
    return apis, list(set(only_apis))

def check_behavioral_source(APIs):
    for API in APIs:
        if API.split('.')[0] in behavioral_sources:
            return True
    return False

def check_browser_fp_sources(APIs):
    for API in APIs:
        if API in browser_fingerprinting_sources:
            return True
    return False

def filter_sources(APIs):
    filtered_list = []
    for API in APIs:
        if API['API'].split('.')[0] in behavioral_sources or API['API'] in browser_fingerprinting_sources:
            filtered_list.append(API)
    return filtered_list


def filter_sinks(APIs):
    filtered_list = []
    for API in APIs:
        if API['API'] in known_sinks:
            filtered_list.append(API)
    return filtered_list


def write_code_to_file(code, filename):
    open(filename, 'w').close()
    # write content of current url js code
    with open(filename, 'a') as jsfile:
        print(code, file=jsfile)

def countAPIs(apis, API_list):
    count = 0
    for api in apis:
        if api in API_list:
            count+=1
    return count

def findMaxAggregationScore(nodes):
    max = 0
    index = -1
    for i,_ in nodes.items():
        if nodes[i]['source_count'] > max:
            max = nodes[i]['source_count']
            index = i
    return max, nodes[index]['source_apis'] if index != -1 else [], nodes[index]['behavioral_count'] if index!= -1 else [], nodes[index]['fp_count'] if index!= -1 else []

def findEventListenersAttached(APIs):
    events = []
    for API in APIs:
        if len(API['API'].split('.')) > 1 and API['API'].split('.')[1] == 'addEventListener' and 'attr' in API:
            if API['attr'] in importantEvents:
                events.append(API['attr'])
    return list(set(events))

def getAllSourceAPIs(APIs):
    behavioral_apis  = []
    fp_apis = []
    for api in APIs:
        if api['API'].split('.')[0] in behavioral_sources:
            behavioral_apis.append(api['API'])
        elif api['API'] in browser_fingerprinting_sources:
            fp_apis.append(api['API'])
    return list(set(behavioral_apis)), list(set(fp_apis))

def insert_into_table(table_name, data):
    columns = data.keys()
    values = []
    
    for column in columns:
        value = data[column]
        
        # Check for invalid values (like empty lists) and replace with None (NULL in SQL)
        if isinstance(value, list) and len(value) == 0:
            values.append(None)
        elif isinstance(value, (dict, list)):
            values.append(json.dumps(value))  # Serialize dicts/lists as JSON for JSONB columns
        else:
            values.append(value)
    
    insert_statement = sql.SQL('INSERT INTO {table} ({fields}) VALUES ({values})').format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        values=sql.SQL(', ').join(sql.Placeholder() * len(columns))
    )

    return insert_statement, values


def findMaxBehavioralScore(nodes):
    max = 0
    index = -1
    for i,_ in nodes.items():
        if nodes[i]['behavioral_count'] > max:
            max = nodes[i]['behavioral_count']
            index = i
    return max, nodes[index]['behavioral_apis'] if index != -1 else []

def findMaxFPScore(nodes):
    max = 0
    index = -1
    for i,_ in nodes.items():
        if nodes[i]['fp_count'] > max:
            max = nodes[i]['fp_count']
            index = i
    return max, nodes[index]['fp_apis'] if index != -1 else []

def calculateAccessCount(APIs):
    behavioral_access_counts = {}
    fingeprinting_access_counts = {}
    for API in APIs:
        api = API['API']
        if api.split('.')[0] in behavioral_sources:
            if api in behavioral_access_counts:
                behavioral_access_counts[api] += 1
            else:
                behavioral_access_counts[api] = 1
        elif api in browser_fingerprinting_sources:
            if api in fingeprinting_access_counts:
                fingeprinting_access_counts[api] += 1
            else:
                fingeprinting_access_counts[api] = 1

    return behavioral_access_counts, fingeprinting_access_counts


def analysis_method(id, url, code, APIs, write_cursor, write_conn, count, lock, write_queue):
    #Ignore scripts belonging to the consent-o-matic extension and devtools
    if "chrome-extension://pogpcelnjdlchjbjcakalbgppnhkondb" in url or "devtools://devtools" in url:
        return

    insertion_data = {
        'script_id': id,
        'script_url': url,
        'code': code,
        'max_api_aggregation_score': -1,
        'behavioral_api_agg_count': -1,
        'fp_api_agg_count': -1,
        'max_aggregated_apis': [],
        'max_behavioral_api_aggregation_score' : -1,
        'aggregated_behavioral_apis': [],
        'max_fingerprinting_api_aggregation_score': -1,
        'aggregated_fingerprinting_apis': [],
        'attached_listeners': [],
        'fingerprinting_source_apis': [],
        'behavioral_source_apis': [],
        'behavioral_source_api_count': 0,
        'fingerprinting_source_api_count': 0,
        'behavioral_apis_access_count' : {},
        'fingerprinting_api_access_count': {},
        'graph_construction_failure': False,
        'dataflow_to_sink': False,
        'apis_going_to_sink': {},
    }

    print('Processing script: ', count)
    
    APIs, unique_APIs = split_APIs(APIs)
    
    #Only check a script if it contains atleast one of the many behavioral sources contained in this file
    if check_behavioral_source(unique_APIs):
        #Temporary file to write script code to
        filename = f"/tmp/exp{count}.js"
        write_code_to_file(code, filename)
        source_APIs = filter_sources(APIs)
        sink_APIs = filter_sinks(APIs)
        insertion_data['behavioral_apis_access_count'], insertion_data['fingerprinting_api_access_count'] = calculateAccessCount(APIs)

        insertion_data['attached_listeners'] = findEventListenersAttached(APIs)
        insertion_data['behavioral_source_apis'], insertion_data['fingerprinting_source_apis'] = getAllSourceAPIs(source_APIs)
        insertion_data['behavioral_source_api_count'] = len(insertion_data['behavioral_source_apis'])
        insertion_data['fingerprinting_source_api_count'] = len(insertion_data['fingerprinting_source_apis'])
        start_time = time.time()
        pdg = get_data_flow(filename, url, lock, benchmarks=dict())
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Took: {elapsed_time:.2f} seconds for {url}")
        if pdg == None:
            print('Unable to generate graph for url: ', url)
            insertion_data['graph_construction_failure'] = True
            insert_statement, values = insert_into_table('multicore_static_info', insertion_data)
            write_queue.put((insert_statement, values))
            return
            
        if (len(sink_APIs) == 0):
            print('File does not call any of the known sinks')

        #Find if they go to known sinks down the whole path
        sink_node_apis = {}
        for api in sink_APIs:
            sink_api_statement_nodes = []
            search_API(pdg, api['offset'],  code[api['offset']: api['offset']+30] if len(code) > api['offset'] + 30 else code[api['offset']: len(code)], api['API'].split('.')[1], sink_api_statement_nodes)
            if sink_api_statement_nodes!=[] and sink_api_statement_nodes[0].get_id() not in sink_node_apis:
                sink_node_apis[sink_api_statement_nodes[0].get_id()] = api['API']

        endpoint_score = {}
        for api in source_APIs:
            source_api = []
            dataflow = []
            if (len(api['API'].split('.')) < 2): # If API is like MouseEvent instead of MouseEvent.screenX keep in mind we are looking for screenX as the API
                continue
            search_API(pdg, api['offset'],  code[api['offset']: api['offset']+30] if len(code) > api['offset'] + 30 else code[api['offset']: len(code)], api['API'].split('.')[1], source_api)
            if source_api != []:
                endp = []
                statement = source_api[0]
                endp += find_dataflow(statement, dataflow)
                old = endp
                endp += dataflow
                for end in list(set(endp)):
                    if end.get_id() not in endpoint_score:
                        endpoint_score[end.get_id()] = {}
                        endpoint_score[end.get_id()]['source_count'] = 1
                        endpoint_score[end.get_id()]['behavioral_count'] = 0
                        endpoint_score[end.get_id()]['behavioral_apis'] = []
                        endpoint_score[end.get_id()]['fp_count'] = 0
                        endpoint_score[end.get_id()]['fp_apis'] = []
                        if api['API'].split('.')[0] in behavioral_sources:
                            endpoint_score[end.get_id()]['behavioral_count'] += 1
                            endpoint_score[end.get_id()]['behavioral_apis'].append(api['API'])
                        else:
                            endpoint_score[end.get_id()]['fp_count'] += 1
                            endpoint_score[end.get_id()]['fp_apis'].append(api['API'])
                        endpoint_score[end.get_id()]['source_apis'] = [api['API']]
                        #If this was the last node in the dataflow path
                        endpoint_score[end.get_id()]['end'] = True if end in old else False
                    else:
                        if(api['API'] not in endpoint_score[end.get_id()]['source_apis']):
                            if (api['API'].split('.')[0] in behavioral_sources):
                                endpoint_score[end.get_id()]['behavioral_count'] += 1
                                endpoint_score[end.get_id()]['behavioral_apis'].append(api['API'])
                            else:
                                endpoint_score[end.get_id()]['fp_count'] += 1
                                endpoint_score[end.get_id()]['fp_apis'].append(api['API'])
                            endpoint_score[end.get_id()]['source_apis'].append(api['API'])
                            endpoint_score[end.get_id()]['source_count'] += 1 

        sink_data = {}
        insertion_data['max_api_aggregation_score'], insertion_data['max_aggregated_apis'], insertion_data['behavioral_api_agg_count'], insertion_data['fp_api_agg_count'] = findMaxAggregationScore(endpoint_score)
        insertion_data['max_behavioral_api_aggregation_score'], insertion_data['aggregated_behavioral_apis'] = findMaxBehavioralScore(endpoint_score)
        insertion_data['max_fingerprinting_api_aggregation_score'], insertion_data['aggregated_fingerprinting_apis'] = findMaxFPScore(endpoint_score)
        for i,j in endpoint_score.items():
            if i in sink_node_apis:
                if sink_node_apis[i] in sink_data:
                    sink_data[sink_node_apis[i]]['source_apis'] += j['source_apis']
                    sink_data[sink_node_apis[i]]['source_apis'] = list(set(sink_data[sink_node_apis[i]]['source_apis']))
                    sink_data[sink_node_apis[i]]['source_count'] = len(sink_data[sink_node_apis[i]]['source_apis'])
                else:
                    sink_data[sink_node_apis[i]] = j
        if len(sink_data) == 0:
            print('No data flow to sinks')
        else:
            insertion_data['dataflow_to_sink'] = True
            insertion_data['apis_going_to_sink'] = sink_data
            sinks = []
            for i,_ in sink_data.items():
                sinks.append(i)

        insert_statement, values = insert_into_table('multicore_static_info', insertion_data)
        write_queue.put((insert_statement, values))
    else:
        print('File with id ' + str(id) + ' contains no relevant sources')


def worker(data, lock, queue):
    write_conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    write_cursor = write_conn.cursor()

    id, url, code, APIs, count = data
    # Call the analysis method
    
    analysis_method(id, url, code, APIs, write_cursor, write_conn, count, lock, queue)

    write_cursor.close()
    write_conn.close()


def batch_writer_worker(queue, batch_size, db_write_function):
    buffer = []
    while True:
        item = queue.get()
        if item is None:  # Sentinel value to indicate end of processing
            if buffer:
                db_write_function(buffer)
            break
        buffer.append(item)
        if len(buffer) >= batch_size:
            db_write_function(buffer)
            buffer = []

def write_batch_to_database(batch):
    write_conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    write_cursor = write_conn.cursor()
    # All insert statements i.e. insert into table fields are same so pick first one
    try:
        insert_statement = batch[0][0]
        values = []
        for elem in batch:
            values.append(elem[1])
        write_cursor.executemany(insert_statement, values)
        write_conn.commit()
    except Exception as e:
        print(f"Error writing batch to database: {e}")

    write_cursor = write_conn.cursor()
    write_cursor.close()
    write_conn.close()


def analyze():
    # Connect to the database
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    write_conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    write_cursor = write_conn.cursor()

    print("Connected to the database.")
    with conn.cursor(name="custom_cursor") as cursor:
        # Create a cursor object using the connection
        cursor.itersize = 1000  # chunk size

        create_table_query = '''
        DROP TABLE IF EXISTS multicore_static_info;
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
            apis_going_to_sink JSONB
        );
        '''

        write_cursor.execute(create_table_query)
        write_conn.commit()
        print("Table 'multicore_static_info' created successfully.")
        
        

        query = "SELECT * FROM script_flow;"
        
        cursor.execute(query)
        # Make sure num_workers less than the CPU count os.cpu_count() due to cpu overload
        num_workers = int(os.cpu_count() / 2)
        batch_size = 10
        print(f"Number of available CPU cores: {num_workers}")
        counter = count()
        tasks = []
        tasks = [(id, url, code, APIs, next(counter)) for id, _, _, code, _, url, APIs, _ in cursor]
        with Manager() as manager:
            lock = manager.Lock()
            queue = manager.Queue()

            writer_process = Process(target=batch_writer_worker, args=(queue, batch_size, write_batch_to_database))
            writer_process.start()

            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
                # Submit tasks to the process pool
                futures = {executor.submit(worker, task, lock, queue): task for task in tasks}
                for future in concurrent.futures.as_completed(futures):
                    task = futures[future]
                    try:
                        # We don't need to do anything with the result, just ensure the task completes
                        future.result()
                        print(f"Task {task[4]} completed successfully")
                    except Exception as exc:
                        print(f"Task {task[4]} generated an exception: {exc}")
                        traceback.print_exc() # Print full error trace for debugging
                        exit(1)
            # Signal writer to end
            queue.put(None)
            # Wait for the writer process to finish
            writer_process.join()

        
        write_cursor.close()
        write_conn.close()
        cursor.close()
        conn.close()
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process multicore static info table and optionally export to CSV.")
    
    # Add argument to handle the optional export
    parser.add_argument('--export', help="Export the `multicore_static_info` table to a CSV at /tmp/<argument>", type=str, required=False)
    
    args = parser.parse_args()

    # Run analysis
    analyze()

    # If the --export argument is provided, export the table to CSV
    if args.export:
        export_table_to_csv(args.export)
