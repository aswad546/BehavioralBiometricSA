from config import BEHAVIORAL_SOURCES, BROWSER_FINGERPRINTING_SOURCES, KNOWN_SINKS, IMPORTANT_EVENTS

def duplicate_api(api, offset, APIs):
    for i in APIs:
        if i['API'] == api and i['offset'] == offset:
            return True
    return False

def split_APIs(APIs):
    """
    Convert API strings into structured dictionaries.
    """
    apis = []
    only_apis = []
    for api in list(set(APIs)):
        construct = {}
        attr = ''
        offset, only_api = api.split(',', 1)
        api_elements = only_api.split('.')
        if len(api_elements) > 2 and api_elements[1] in ['addEventListener', 'setAttribute'] and len(api_elements) == 3:
            only_api = '.'.join(api_elements[:2])
            attr = api_elements[2]
        elif len(api_elements) == 2 and api_elements[1] in ['addEventListener', 'setAttribute']:
            continue
        construct['offset'] = int(offset)
        construct['API'] = only_api
        if attr:
            construct['attr'] = attr
        apis.append(construct)
        only_apis.append(construct['API'])
    return apis, list(set(only_apis))

def check_behavioral_source(APIs):
    for API in APIs:
        if API in BEHAVIORAL_SOURCES:
            return True
    return False

def check_browser_fp_sources(APIs):
    for API in APIs:
        if API in BROWSER_FINGERPRINTING_SOURCES:
            return True
    return False

def filter_sources(APIs):
    return [API for API in APIs if API['API'] in BEHAVIORAL_SOURCES or API['API'] in BROWSER_FINGERPRINTING_SOURCES]

def filter_sinks(APIs):
    return [API for API in APIs if API['API'] in KNOWN_SINKS]

def write_code_to_file(code, filename):
    with open(filename, 'w') as jsfile:
        jsfile.write(code)

def count_APIs(apis, API_list):
    return sum(1 for api in apis if api in API_list)

def find_max_aggregation_score(nodes):
    max_val = 0
    index = -1
    for key, node in nodes.items():
        if node['source_count'] > max_val:
            max_val = node['source_count']
            index = key
    if index != -1:
        return max_val, nodes[index]['source_apis'], nodes[index]['behavioral_count'], nodes[index]['fp_count']
    return max_val, [], 0, 0

def find_event_listeners_attached(APIs):
    events = []
    for API in APIs:
        parts = API['API'].split('.')
        if len(parts) > 1 and parts[1] == 'addEventListener' and 'attr' in API:
            if API['attr'] in IMPORTANT_EVENTS:
                events.append(API['attr'])
    return list(set(events))

def get_all_source_APIs(APIs):
    behavioral_apis = []
    fp_apis = []
    for api in APIs:
        if api['API'] in BEHAVIORAL_SOURCES:
            behavioral_apis.append(api['API'])
        elif api['API'] in BROWSER_FINGERPRINTING_SOURCES:
            fp_apis.append(api['API'])
    return list(set(behavioral_apis)), list(set(fp_apis))

def find_max_behavioral_score(nodes):
    max_val = 0
    index = -1
    for key, node in nodes.items():
        if node['behavioral_count'] > max_val:
            max_val = node['behavioral_count']
            index = key
    if index != -1:
        return max_val, nodes[index]['behavioral_apis']
    return max_val, []

def find_max_fp_score(nodes):
    max_val = 0
    index = -1
    for key, node in nodes.items():
        if node['fp_count'] > max_val:
            max_val = node['fp_count']
            index = key
    if index != -1:
        return max_val, nodes[index]['fp_apis']
    return max_val, []

def calculate_access_count(APIs):
    behavioral_access = {}
    fp_access = {}
    for API in APIs:
        api_name = API['API']
        if api_name in BEHAVIORAL_SOURCES:
            behavioral_access[api_name] = behavioral_access.get(api_name, 0) + 1
        elif api_name in BROWSER_FINGERPRINTING_SOURCES:
            fp_access[api_name] = fp_access.get(api_name, 0) + 1
    return behavioral_access, fp_access
