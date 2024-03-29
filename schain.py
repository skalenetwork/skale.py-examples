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
from ima_predeployed.generator import generate_abi
from skale import Skale, SkaleIma
from skale.dataclasses.skaled_ports import SkaledPorts
# from skale.schain_config.generator import get_nodes_for_schain
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.main import add_test_schain_type

from skale.utils.constants import LONG_LINE
from skale.utils.helper import ip_from_bytes
from skale.utils.random_names.generator import generate_random_schain_name
from skale.utils.web3_utils import to_checksum_address

from skale.schain_config.generator import get_schain_nodes_with_schains
from skale.schain_config.ports_allocation import get_schain_base_port_on_node


from utils import create_account, init_wallet
from config import ENDPOINT, ABI_FILEPATH, IMA_ABI_FILEPATH


init_default_logger()
logger = logging.getLogger(__name__)


TEST_SRW_FUND_VALUE = 300000000000000000


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


def get_node_schain_ports_info(base_port):
    return {
        rec.name: base_port + rec.value
        for rec in SkaledPorts
    }


def get_schain_info(skale, schain_name):
    schain_struct = skale.schains.get_by_name(schain_name)
    schain_nodes_with_schains = get_schain_nodes_with_schains(
        skale,
        schain_name
    )

    for i, node_info in enumerate(schain_nodes_with_schains, 1):
        base_port = get_schain_base_port_on_node(
            node_info['schains'],
            schain_name, node_info['port']
        )

        node_info['ip'] = ip_from_bytes(node_info['ip'])
        node_info['publicIP'] = ip_from_bytes(node_info['publicIP'])
        ports = get_node_schain_ports_info(base_port)
        node_info['basePort'] = base_port
        node_info.pop('port')
        node_info.pop('schains')
        node_info['ports'] = ports
        node_info['http_endpoint'] = f'http://{node_info["publicIP"]}:{node_info["ports"]["HTTP_JSON"]}'  # noqa
        node_info['https_endpoint'] = f'http://{node_info["publicIP"]}:{node_info["ports"]["HTTPS_JSON"]}'  # noqa

    return {
        'schain_struct': schain_struct,
        'schain_nodes': schain_nodes_with_schains
    }


def create_schain(
    skale,
    wallet,
    nodes_type_name,
    by_foundation=False,
    skale_ima=None
):
    lifetime_seconds = 12 * 3600  # 12 hours
    nodes_type_idx = int(SchainType[nodes_type_name].value)
    nodes_type_idx = 1
    print(nodes_type_idx)
    schain_name = generate_random_schain_name()
    if by_foundation:
        skale.schains.grant_role(
            skale.schains.schain_creator_role(),
            skale.wallet.address
        )
        skale.schains.add_schain_by_foundation(
            lifetime_seconds,
            nodes_type_idx,
            0,
            schain_name,
            wait_for=True,
            value=TEST_SRW_FUND_VALUE
        )
    else:
        price_in_wei = skale.schains.get_schain_price(nodes_type_idx,
                                                      lifetime_seconds)
        skale.manager.create_schain(
            lifetime_seconds,
            nodes_type_idx,
            price_in_wei,
            schain_name,
            skip_dry_run=True,
            gas_limit=7500000
        )
    if skale_ima:
        schain_ima_abi = generate_abi()
        skale_ima.linker.connect_schain(
            schain_name,
            [
                schain_ima_abi['community_locker_address'],
                schain_ima_abi['token_manager_eth_address'],
                schain_ima_abi['token_manager_erc20_address'],
                schain_ima_abi['token_manager_erc721_address'],
                schain_ima_abi['token_manager_erc1155_address']
            ]
        )

    return get_schain_info(skale, schain_name)


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
@click.argument('amount', default=1)
@click.option('--save-to', default='./creds',
              help='Directory to save schains data')
@click.option('--type', default=SchainType.TEST2.name,
              type=click.Choice([n_type.name for n_type in SchainType],
                                case_sensitive=False),
              help='Nodes type (tiny/small/medium/test2/test4) for schain')
@click.pass_context
def create_by_foundation(ctx, amount, save_to, type):
    """
    Command that creates schains
    from foundation account specified by ETH_PRIVATE_KEY
    """
    skale = ctx.obj['skale']
    skale_ima = SkaleIma(ENDPOINT, IMA_ABI_FILEPATH, skale.wallet)

    for i in range(amount):
        schain_info = create_schain(skale, skale.wallet, type,
                                    by_foundation=True, skale_ima=skale_ima)
        save_info(i, schain_info, skale.wallet, save_to)
        logger.info(LONG_LINE)
    show_all_schains_names(skale)


@main.command()
@click.argument('schain_name')
@click.pass_context
def remove(ctx, schain_name):
    """ Command that removes schain by name """
    skale = ctx.obj['skale']
    skale.manager.delete_schain(schain_name, wait_for=True,
                                gas_price=4500000000)
    print(f'sChain {schain_name} removed!')


@main.command()
@click.pass_context
def remove_all(ctx):
    """ Command that removes all schains """
    skale = ctx.obj['skale']
    cnt = 0
    for sname in get_all_schains_names(skale):
        skale.manager.delete_schain(sname)
        cnt += 1
    print(f'Success. {cnt} schains were removed')


@main.command()
@click.pass_context
def show(ctx):
    """ Command that show all schains ids """
    skale = ctx.obj['skale']
    # from skale.utils.contracts_provision.main import add_test_permissions
    # add_test_permissions(skale)
    show_all_schains_names(skale)


@main.command()
@click.pass_context
@click.argument('schain_name')
def info(ctx, schain_name):
    """ Command that show all schains ids """
    skale = ctx.obj['skale']
    info = get_schain_info(skale, schain_name)
    print(json.dumps(info, indent=2))


@main.command()
@click.pass_context
@click.argument('address')
def grant_role(ctx, address):
    """ Command for granting creator role to address """
    skale = ctx.obj['skale']
    address = to_checksum_address(address)
    skale.schains.grant_role(skale.schains.schain_creator_role(),
                             address)
    print('Success')


@main.command()
@click.pass_context
@click.argument('schain_name')
def is_last_dkg_successful(ctx, schain_name):
    """ Checks if the last dkg procedure for schain was succesful """
    skale = ctx.obj['skale']
    group_index = skale.schains.name_to_id(schain_name)
    res = skale.dkg.is_last_dkg_successful(group_index)
    print(res)


@main.command()
@click.pass_context
def add_test_type(ctx):
    skale = ctx.obj['skale']
    res = add_test_schain_type(skale)
    print(res)


@main.command()
@click.pass_context
def add_types(ctx):
    skale = ctx.obj['skale']
    for p, n in [(1, 16), (8, 16), (128, 16), (0, 2), (0, 4)]:
        skale.schains_internal.add_schain_type(p, n)


@main.command()
@click.pass_context
def types(ctx):
    skale = ctx.obj['skale']
    print('Schain types: ')
    n = skale.schains_internal.contract.functions.numberOfSchainTypes().call()
    for i in range(1, n + 1):
        print(skale.schains_internal.contract.functions.schainTypes(i).call())


if __name__ == "__main__":
    main()
