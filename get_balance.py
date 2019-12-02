import os
from skale import Skale
from skale.wallets import RPCWallet
from config import ENDPOINT, ABI_FILEPATH

TM_URL = os.environ['TM_URL']

wallet = RPCWallet(TM_URL)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)

print('Address: ', wallet.address)
eth_balance_wei = skale.web3.eth.getBalance(wallet.address)
skale_balance_wei = skale.token.get_balance(wallet.address)

print('eth.wei: ', str(eth_balance_wei))
print('skale.wei: ', str(skale_balance_wei))
print('eth.ether: ', str(skale.web3.fromWei(eth_balance_wei, 'ether')))
print('skale.wei: ', str(skale.web3.fromWei(skale_balance_wei, 'ether')))
