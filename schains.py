#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Commands to manage SKALE schains """

import datetime
import json
import logging
import os
from enum import Enum

import click

from skale import Skale
from skale.schain_config.generator import get_nodes_for_schain_config
from skale.utils.helper import init_default_logger
from skale.utils.account_tools import (check_ether_balance,
                                       check_skale_balance, generate_account,
                                       send_ether, send_tokens)
from skale.utils.constants import LONG_LINE
from skale.utils.random_names.generator import generate_random_schain_name
from skale.wallets import Web3Wallet
from utils import init_wallet

from config import ENDPOINT, ABI_FILEPATH, ETH_PRIVATE_KEY


init_default_logger()
logger = logging.getLogger(__name__)


class SchainType(Enum):
    TINY = 1
    SMALL = 2
    MEDIUM = 3
    TEST2 = 4
    TEST4 = 5


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, help='abi file')
@click.pass_context
def main(ctx, endpoint, abi_filepath):
    ctx.ensure_object(dict)
    wallet = init_wallet(endpoint)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath, wallet)


def save_info(schain_index, schain_info=None, wallet=None,
              private_key=None, data_dir=None):
    time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    schain_name = schain_info['schain_struct']['name']
    filename = f'wallet_{schain_index}_{schain_name}_{time}.json'
    info = {
        'schain_info': schain_info,
        'wallet': {
            'address': wallet.address,
            'public_key': wallet.public_key,
            'private_key': private_key
        }
    }
    if data_dir:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        filepath = os.path.join(data_dir, filename)
        print(filepath)
        with open(filepath, 'w') as outfile:
            logger.info(f'Saving info to {filename}')
            json.dump(info, outfile, indent=4)


def get_all_schains_names(skale):
    schains_ids = skale.schains_internal.get_all_schains_ids()
    names = [skale.schains.get(sid).get('name')
             for sid in schains_ids]
    return names


def show_all_schains_names(skale):
    schain_names = get_all_schains_names(skale)
    print('\n'.join(schain_names))


def get_schain_info(skale, schain_name):
    schain_struct = skale.schains.get_by_name(schain_name)
    schain_nodes = get_nodes_for_schain_config(skale, schain_name)
    return {'schain_struct': schain_struct, 'schain_nodes': schain_nodes}


def create_schain(skale, wallet, nodes_type_name):
    lifetime_seconds = 12 * 3600  # 12 hours
    nodes_type_idx = int(SchainType[nodes_type_name].value)
    print(nodes_type_idx)
    schain_name = generate_random_schain_name()
    price_in_wei = skale.schains.get_schain_price(nodes_type_idx,
                                                  lifetime_seconds)
    skale.manager.create_schain(
        lifetime_seconds,
        nodes_type_idx,
        price_in_wei,
        schain_name,
        wait_for=True
    )
    return get_schain_info(skale, schain_name)


def create_account(skale, skale_amount, eth_amount, debug=True):
    base_wallet = Web3Wallet(ETH_PRIVATE_KEY, skale.web3)
    wallet_dict = generate_account(skale.web3)
    wallet = Web3Wallet(wallet_dict['private_key'], skale.web3)

    send_tokens(skale, base_wallet, wallet.address, skale_amount, debug)
    send_ether(skale.web3, base_wallet, wallet.address, eth_amount, debug)

    if debug:
        check_ether_balance(skale.web3, wallet.address)
        check_skale_balance(skale, wallet.address)
    return wallet, wallet_dict['private_key']


def show_all_schain_ids(skale):
    schains_number = skale.schains_internal.get_schains_number()
    print(f'There are {schains_number} schains')
    schains_ids = skale.schains_internal.get_all_schains_ids()
    print(schains_ids)


@main.command()
@click.argument('amount', default=1)
@click.option('--save-to', default='./creds',
              help='Directory to save schains data')
@click.option('--skale-amount', default=1000,
              help='Amount of skale to add to new accounts')
@click.option('--eth-amount', default=10,
              help='Amount of eth to add to new accounts')
@click.option('--type', default=SchainType.TEST2.name,
              type=click.Choice([n_type.name for n_type in SchainType],
                                case_sensitive=False),
              help='Nodes type (tiny/small/medium/test2/test4) for schain')
@click.pass_context
def create_with_account(ctx, amount, save_to, skale_amount, eth_amount, type):
    """ Command that creates new accounts with schains """
    skale = ctx.obj['skale']
    print(save_to)
    for i in range(amount):
        wallet, private_key = create_account(skale, skale_amount, eth_amount)
        schain_info = create_schain(skale, wallet, type)
        save_info(i, schain_info, wallet, private_key, save_to)
        logger.info(LONG_LINE)
    show_all_schain_ids(skale)


@main.command()
@click.argument('amount', default=1)
@click.option('--save-to', default='./creds',
              help='Directory to save schains data')
@click.option('--type', default=SchainType.TEST2.name,
              type=click.Choice([n_type.name for n_type in SchainType],
                                case_sensitive=False),
              help='Nodes type (tiny/small/medium/test2/test4) for schain')
@click.pass_context
def create(ctx, amount, save_to, type):
    """
    Command that creates schains from account specified by ETH_PRIVATE_KEY
    """
    skale = ctx.obj['skale']
    for i in range(amount):
        schain_info = create_schain(skale, skale.wallet, type)
        save_info(i, schain_info, skale.wallet, save_to)
        logger.info(LONG_LINE)
    show_all_schains_names(skale)


@main.command()
@click.argument('schain_name')
@click.pass_context
def remove(ctx, schain_name):
    """ Command that removes schain by name """
    skale = ctx.obj['skale']
    skale.manager.delete_schain(schain_name, wait_for=True)
    print(f'sChain {schain_name} removed!')


@main.command()
@click.pass_context
def show(ctx):
    """ Command that show all schains ids """
    skale = ctx.obj['skale']
    show_all_schains_names(skale)


@main.command()
@click.pass_context
@click.argument('schain_name')
def info(ctx, schain_name):
    """ Command that show all schains ids """
    skale = ctx.obj['skale']
    info = get_schain_info(skale, schain_name)
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
