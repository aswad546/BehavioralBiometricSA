from pymongo import MongoClient
from psycopg2 import sql
import psycopg2
import json

def pre_proc(apis):
    real_apis = []
    only_apis = []
    
    for i in apis:
        splitted = i.split(',')
        if len(splitted) == 2:
            only_apis.append(splitted[1])
            real_apis.append(i)
            continue

        idx = i.index(",")+1
        sequence = i[1:idx]
        i = i[idx:]
        
        idx = i.index(",")+1
        api = i[idx:]
        only_apis.append(api)
        real_apis.append(sequence+api)
    
    return only_apis,real_apis

def FPIdldata():
    std_api = []
    with open("/home/vagrant/BehavioralBiometricSA/idldata.json") as f:
        data = json.load(f)

    for i in data:
        if data[str(i)] is not None:
            if "members" in data[str(i)]:
                for ele in data[str(i)]["members"]:
                    std_api.append(str(i) + "." + str(ele))
                if "parent" in data[str(i)]:
                    curr = data[str(i)]['parent']
                    while (curr != None):
                        if "members" in data[str(curr)]:
                            for api in data[str(curr)]["members"]:
                                std_api.append(str(i)+"."+str(api))
                        if "parent" in data[str(curr)]:
                            curr = data[str(curr)]['parent']
                        else:
                            break
            else:
                for ele in data[str(i)].values():
                    std_api.append(str(i) + "." + str(ele))
    return std_api


def insert_into_table(table_name, data):
    if not data:
        return None, []

    # Assume all dictionaries have the same keys
    columns = data[0].keys()
    
    # Prepare the insert statement
    insert_statement = sql.SQL('INSERT INTO {table} ({fields}) VALUES ').format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns))
    )
    
    # Collect values and placeholders
    values = []
    placeholders = []
    for data in data:
        row_values = [json.dumps(data[column]) if isinstance(data[column], (dict, list)) else data[column] for column in columns]
        values.extend(row_values)
        placeholders.append(sql.SQL('({})').format(sql.SQL(', ').join(sql.Placeholder() * len(columns))))

    # Combine the placeholders into the insert statement
    insert_statement = insert_statement + sql.SQL(', ').join(placeholders)
    
    return insert_statement, values


if __name__ == "__main__":
    std_api = FPIdldata()
    try:
        write_conn = psycopg2.connect(
            dbname='vv8_backend',
            user='vv8',
            password='vv8',
            host='localhost',
            port='5434'
        )
        write_cursor = write_conn.cursor()
        # connect to Postgres
        con = psycopg2.connect(
            dbname='vv8_backend',
            user='vv8',
            password='vv8',
            host='localhost',
            port='5434'
        )

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS webidl_apis (
            id SERIAL,
            script_url TEXT,
            unique_browser_apis JSONB
        );
        '''

        write_cursor.execute(create_table_query)
        write_conn.commit()
        print("Table 'webidl_apis' created successfully or already exists.")

        with con.cursor(name="custom_cursor") as cursor:
            cursor.itersize = 1000  # chunk size
            query = "SELECT * FROM script_flow;"
            cursor.execute(query)
            count = 0
            # Iterate every API sequence per execution context
            finalData = []
            for id, _, _, _, _, url, APIs, _ in cursor:
                if "chrome-extension://pogpcelnjdlchjbjcakalbgppnhkondb" in url or "devtools://devtools" in url:
                    continue
                insertion_data = {
                    'id': id,
                    'script_url': url,
                    'unique_browser_apis': [],
                }
                print("Checking APIs for script :", url)
                apis = []
                only_apis,real_apis = pre_proc(APIs)
                api_uni = list(set(only_apis))
                for i in api_uni:
                    if i in std_api:
                        apis.append(i)
                insertion_data['unique_browser_apis'] = apis
                finalData.append(insertion_data)
            insert_statement, values = insert_into_table('webidl_apis', finalData)
            write_cursor.execute(insert_statement, values)
            write_conn.commit()
    except (Exception) as e:
        print("Exception during connection", e)
        # exit(0) 
    finally:
        cursor.close()
        con.close()
        write_cursor.close()
        write_conn.close()