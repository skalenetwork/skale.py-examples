import logging

import click
from skale import Skale
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import check_receipt

from web3 import Web3
from config import ENDPOINT, ABI_FILEPATH
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


def token_transfer(skale, address_to, tokens_amount):
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    print('Balance from before {}'.format(balance_from_before / ETH_IN_WEI))
    print('Balance to before {}'.format(balance_to_before / ETH_IN_WEI))

    receipt = skale.token.transfer(address_to, tokens_amount, wait_for=True)

    balance_from_after = skale.token.get_balance(address_from)
    balance_to_after = skale.token.get_balance(address_to)
    print('Balance from after {}'.format(balance_from_after / ETH_IN_WEI))
    print('Balance to after {}'.format(balance_to_after / ETH_IN_WEI))
    print(f'Diff from account {balance_from_after - balance_from_before}')
    print(f'Diff to account {balance_to_after - balance_to_before}')
    return receipt


@main.command()
@click.pass_context
@click.argument('address_to')
@click.argument('tokens_amount', type=int)
def transfer(ctx, address_to, tokens_amount):
    """ Command for transfering tokens to address """
    skale = ctx.obj['skale']
    receipt = token_transfer(skale, address_to, tokens_amount * ETH_IN_WEI)
    check_receipt(receipt)


def show_skl_balance(skale):
    address = Web3.toChecksumAddress(skale.wallet.address)
    balance = skale.token.get_balance(address)
    print('Balance {} SKL'.format(balance / ETH_IN_WEI))


@main.command()
@click.pass_context
def show(ctx):
    skale = ctx.obj['skale']
    show_skl_balance(skale)


if __name__ == "__main__":
    main()
