import requests
import sys
import csv
import time
import socket
from operator import itemgetter
from concurrent.futures import as_completed, ThreadPoolExecutor


POST_REQUEST_TIMEOUT = 30

SCHAIN_INFO = {}

def is_port_open(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(2)
   try:
      s.connect((ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False


def post_request(url, json, cookies=None):
    try:
        return requests.post(url, json=json, cookies=cookies,
                             timeout=POST_REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as err:
        print(f'Post request failed with: {err}')
        return None


def make_rpc_call(http_endpoint, method, params=[]) -> bool:
    res = post_request(
        http_endpoint,
        json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    )
    if res and res.json():
        return res.json()
        

def save_csv(schain_name, rows):
    report_filename = f'schain_{schain_name}_data.csv'
    with open(report_filename, mode='w') as employee_file:
        writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)


def hex_to_int(hex_val):
    return int(hex_val, 16)


def check_all_ports(ip, ports):
    ports_res = []
    for port_name in ports:
        ports_res.append(is_port_open(ip, ports[port_name]))
    return ports_res


def process_node(schain_node):
    print(f'Processing node [{schain_node["id"]}] {schain_node["name"]}...')
    start_time = time.time()
    response = make_rpc_call(schain_node['http_endpoint'], 'eth_getBlockByNumber', ['latest', False])
    end_time = time.time()
    req_time = end_time - start_time
    if response:
        block_number = hex_to_int(response['result']['number'])
        block_timestamp = hex_to_int(response['result']['timestamp'])
    else:
        block_number, block_timestamp, req_time = '-', '-', '-'
    ports_res = check_all_ports(schain_node['ip'], schain_node['ports'])
    return [
        schain_node["id"],
        schain_node["name"],
        schain_node['http_endpoint'],
        block_number,
        block_timestamp,
        req_time
    ] + ports_res


if __name__ == "__main__":
    schain_nodes_info = SCHAIN_INFO['schain_nodes']

    if len(sys.argv) > 1:
        current_node_id = sys.argv[1]
        schain_nodes_info = [node for node in schain_nodes_info if str(node['id']) != str(current_node_id)]

    rows = []
    header = ['node_id', 'node_name', 'http_endpoint', 'block_number', 'block_timestamp', 'req_time'] + list(schain_nodes_info[0]['ports'].keys())

    with ThreadPoolExecutor(max_workers=max(1, len(schain_nodes_info))) as executor:
        futures = [
            executor.submit(
                process_node,
                schain_node
            )
            for schain_node in schain_nodes_info
        ]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
    rows = sorted(rows, key=itemgetter(0))
    rows.insert(0, header)
    save_csv(SCHAIN_INFO['schain_struct']['name'], rows)
