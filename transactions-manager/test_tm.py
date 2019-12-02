import threading
import os
from skale import Skale
from skale.wallets import RPCWallet
from config import ENDPOINT, ABI_FILEPATH
from utils import generate_random_node_data
from skale.utils.web3_utils import wait_receipt

TM_URL = os.environ['TM_URL']

wallet = RPCWallet(TM_URL)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)


def main():
    monitors = []
    for _ in range(0, 5):
        monitor = threading.Thread(target=create_nodes, daemon=True)
        monitor.start()
        monitors.append(monitor)
    for monitor in monitors:
        monitor.join()


def create_nodes():
    for _ in range(0, 100):
        create_node()


def create_node():
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    res = skale.manager.create_node(ip, port, name, public_ip)
    receipt = wait_receipt(skale.web3, res['tx'])
    print(receipt)
    return receipt


if __name__ == "__main__":
    print('Address: ', wallet.address)
    create_node()
    # main()
