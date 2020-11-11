import logging

import click
from skale import Skale
from skale.utils.account_tools import check_ether_balance, send_ether
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import private_key_to_address
from web3 import Web3

from config import ENDPOINT, ABI_FILEPATH
from schains import create_account
from utils import init_wallet

init_default_logger()
logger = logging.getLogger(__name__)

ETH_IN_WEI = 10 ** 18


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, help='abi file')
@click.pass_context
def main(ctx, endpoint, abi_filepath):
    ctx.ensure_object(dict)
    wallet = init_wallet(endpoint)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath, wallet)


@main.command()
@click.argument('private_key')
def address_from_key(private_key):
    print(private_key_to_address(private_key))


@main.command()
@click.pass_context
def send_funds(ctx):
    skale = ctx.obj['skale']
    skale_amount = 2000
    eth_amount = 3
    wallet, private_key = create_account(skale, skale_amount, eth_amount)
    print(wallet.address)
    print(private_key)


def skale_token_transfer(skale, address_to, tokens_amount):
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    print(
        'Balance SKL from before {}'.format(balance_from_before / ETH_IN_WEI)
    )
    print('Balance SKL to before {}'.format(balance_to_before / ETH_IN_WEI))

    tx_res = skale.token.transfer(address_to, tokens_amount, wait_for=True)
    tx_res.raise_for_status()

    balance_from_after = skale.token.get_balance(address_from)
    balance_to_after = skale.token.get_balance(address_to)
    print('Balance SKL from after {}'.format(balance_from_after / ETH_IN_WEI))
    print('Balance SKL to after {}'.format(balance_to_after / ETH_IN_WEI))
    print(f'Diff SKL from account {balance_from_after - balance_from_before}')
    print(f'Diff SKL to account {balance_to_after - balance_to_before}')


def eth_token_transfer(web3, wallet, address_to, eth_amount):
    address_from = Web3.toChecksumAddress(wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = check_ether_balance(web3, address_from)
    balance_to_before = check_ether_balance(web3, address_to)
    print(
        'Balance ETH from before {}'.format(balance_from_before)
    )
    print('Balance ETH to before {}'.format(balance_to_before))

    send_ether(web3, wallet, address_to, eth_amount, wait_for=True)

    balance_from_after = check_ether_balance(web3, address_from)
    balance_to_after = check_ether_balance(web3, address_to)
    print('Balance ETH from after {}'.format(balance_from_after))
    print('Balance ETH to after {}'.format(balance_to_after))
    print(f'Diff ETH from account {balance_from_after - balance_from_before}')
    print(f'Diff ETH to account {balance_to_after - balance_to_before}')
    pass


@main.command()
@click.pass_context
@click.argument('address_to')
@click.argument('tokens_amount', type=int)
def skale_transfer(ctx, address_to, tokens_amount):
    """ Command for transfering SKL to account specified by address_to """
    skale = ctx.obj['skale']
    skale_token_transfer(skale, address_to, tokens_amount * ETH_IN_WEI)
    print('Success')


@main.command()
@click.pass_context
@click.argument('address_to')
@click.argument('eth_amount', type=float)
def eth_transfer(ctx, address_to, eth_amount):
    """ Command for transfering ETH to account specified by address_to """
    skale = ctx.obj['skale']
    eth_token_transfer(skale.web3, skale.wallet, address_to, eth_amount)
    print('Success')


def show_wallet_info(skale, address=None):
    address = address or skale.wallet.address
    chs_address = Web3.toChecksumAddress(address)
    skale_balance = skale.token.get_balance(chs_address)
    eth_balance = check_ether_balance(skale.web3, chs_address)
    print(f'Address: {address}')
    print('Balance {} SKL'.format(skale_balance / ETH_IN_WEI))
    print('Balance {} ETH'.format(eth_balance))


@main.command()
@click.option('--address', help='Address to check account', default=None)
@click.pass_context
def show(ctx, address):
    """ Command for displaying information about account """
    skale = ctx.obj['skale']
    show_wallet_info(skale, address)


if __name__ == "__main__":
    main()
