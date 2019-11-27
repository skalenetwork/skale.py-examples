import os
import skale.utils.helper as Helper
from skale.utils.helper import ip_from_bytes
from skale import Skale
from skale.wallets import RPCWallet

from config import ENDPOINT, ABI_FILEPATH

Helper.init_default_logger()

TM_URL = os.environ['TM_URL']
wallet = RPCWallet(TM_URL)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)


for _ in range(0, 1000000):
    nodes_ips = skale.nodes_data.get_active_node_ips()
    ips = []
    for ip in nodes_ips:
        ips.append(ip_from_bytes(ip))

    print('====')
    print('IPS', ips)
    print('====')
