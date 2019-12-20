import click

from web3 import Web3
from skale import Skale
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import check_receipt, wait_receipt

from utils import init_wallet
from config import ENDPOINT, ABI_FILEPATH

init_default_logger()


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
    print('Balance from before {}'.format(balance_from_before))
    print('Balance to before {}'.format(balance_to_before))

    res = skale.token.transfer(address_to, tokens_amount)
    receipt = wait_receipt(skale.web3, res['tx'])
    check_receipt(receipt)

    balance_from_after = skale.token.get_balance(address_from)
    balance_to_after = skale.token.get_balance(address_to)
    print('Balance from after {}'.format(balance_from_after))
    print('Balance to after {}'.format(balance_to_after))
    diff_from = balance_from_before - balance_from_after
    diff_to = balance_to_after - balance_to_before
    assert diff_from == diff_to
    return receipt


@main.command()
@click.pass_context
@click.argument('address_to')
@click.argument('tokens_amount', type=int)
def transfer(ctx, address_to, tokens_amount):
    """ Command for transfering tokens to address """
    skale = ctx.obj['skale']
    token_transfer(skale, address_to, tokens_amount)


def show_skl_balance(skale):
    address = Web3.toChecksumAddress(skale.wallet.address)
    balance = skale.token.get_balance(address)
    print('Balance {} SKL'.format(balance))


@main.command()
@click.pass_context
def show(ctx):
    skale = ctx.obj['skale']
    show_skl_balance(skale)


if __name__ == "__main__":
    main()
