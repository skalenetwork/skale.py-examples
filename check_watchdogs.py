import socket
import logging

from skale import Skale
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.helper import ip_from_bytes, init_default_logger

from skale.contracts.manager.nodes import NodeStatus

from config import ENDPOINT, ABI_FILEPATH
from utils import init_wallet

import time


logger = logging.getLogger(__name__)

WATCHDOG_PORT = 3009


def is_port_open(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(1)
   try:
      s.connect((ip, int(port)))
      s.shutdown(1)
      return True
   except:
      return False


def check_validator_nodes(skale, node_id):
    try:
        node = skale.nodes.get(node_id)
        node_ids = skale.nodes.get_validator_node_indices(node['validator_id'])

        try: 
            node_ids.remove(node_id)
        except ValueError:
            logger.warning(f'node_id: {node_id} was not found in validator nodes: {node_ids}')

        res = []
        for node_id in node_ids:
            if skale.nodes.get_node_status(node_id) == NodeStatus.ACTIVE.value:
                ip_bytes = skale.nodes.contract.functions.getNodeIP(node_id).call()
                ip = ip_from_bytes(ip_bytes)
                res.append([node_id, ip, is_port_open(ip, WATCHDOG_PORT)])
        logger.info(f'node_id: {node_id}, res: {res}')
    except Exception as err:
        return {'status': 1, 'errors': [err]}
    return {'status': 0, 'data': res}


if __name__ == "__main__":
    init_default_logger()
    wallet = init_wallet(ENDPOINT)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)

    node_id = 1    
    start_time = time.time()
    res = check_validator_nodes(skale, node_id)
    print(res)
    end_time = time.time()
    print(f'time: {end_time - start_time}')