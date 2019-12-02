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
""" Commands to manage SKALE nodes """

import json
import os

import click

from skale import Skale
from skale.utils.web3_utils import wait_receipt, check_receipt
from skale.utils.helper import ip_from_bytes, init_default_logger
from skale.utils.constants import LONG_LINE

from utils import init_wallet, generate_random_node_data
from config import ENDPOINT, ABI_FILEPATH


init_default_logger()


def create_node(skale):
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    res = skale.manager.create_node(ip, port, name, public_ip)
    receipt = wait_receipt(skale.web3, res['tx'])
    return receipt


def remove_node(skale, name):
    node_id = skale.nodes_data.node_name_to_index(name)
    res = skale.manager.delete_node_by_root(node_id)
    receipt = wait_receipt(skale.web3, res['tx'])
    check_receipt(receipt)
    print(f'Node {name} was successfully removed')


def remove_active_nodes(skale):
    for node_id in skale.nodes_data.get_active_node_ids():
        node = skale.nodes_data.get(node_id)
        node_name = node.get('name')
        if node_name:
            remove_node(skale, node_name)


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='Skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, type=click.Path(),
              help='abi file')
@click.pass_context
def main(ctx, endpoint, abi_filepath):
    ctx.ensure_object(dict)
    wallet = init_wallet(endpoint)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath, wallet)


@main.command()
@click.argument('amount', default=1)
@click.pass_context
def create(ctx, amount):
    """ Command to create given amount of nodes """
    skale = ctx.obj['skale']

    print(f'Creating {amount} nodes...')
    for i in range(int(amount)):
        print(LONG_LINE)
        print(f'Creating {i+1}/{amount} node...')
        receipt = create_node(skale)
        check_receipt(receipt)


@main.command()
@click.option('--save-to', default='./schains-by-node',
              help='Directory to save full schains data by specific node')
@click.pass_context
def schains_by_node(ctx, save_to):
    """ Command that shows schains for active nodes """
    skale = ctx.obj['skale']

    schains = []
    sizes = []
    for node_id in skale.nodes_data.get_active_node_ids():
        node = skale.nodes_data.get(node_id)

        node_struct = {
            'name': node['name'],
            'ip': ip_from_bytes(node['ip']),
            'basePort': node['port'],
            'publicIP': ip_from_bytes(node['publicIP']),
        }

        schains_for_node = skale.schains_data.get_schains_for_node(node_id)
        schains.append({
            'schains': schains_for_node,
            'amount': len(schains_for_node),
            'node': node_struct
        })
        sizes.append(len(schains_for_node))

    if not os.path.exists(save_to):
        os.makedirs(save_to)

    filepath = os.path.join(save_to, 'schains_data.json')
    with open(filepath, 'w') as outfile:
        json.dump(schains, outfile)

    print('sChains on each node:')
    print(sizes)


@main.command()
@click.pass_context
def show(ctx):
    """ Command to show id name and ip of active nodes """
    skale = ctx.obj['skale']

    nodes_data = []
    for _id in skale.nodes_data.get_active_node_ids():
        data = skale.nodes_data.get(_id)
        name = data.get('name')
        ip = ip_from_bytes(data.get('ip'))
        pub_key = skale.web3.toHex(data['publicKey'])
        port = data.get('port')
        nodes_data.append((_id, name, ip, port, pub_key))
    print(nodes_data)


@main.command()
@click.argument('node-name')
@click.pass_context
def remove(ctx, node_name):
    """ Command to remove node specified by name """
    skale = ctx.obj['skale']
    remove_node(skale, node_name)


@main.command()
@click.pass_context
def remove_all(ctx):
    """ Command to remove node specified by name """
    skale = ctx.obj['skale']
    remove_active_nodes(skale)


if __name__ == "__main__":
    main()
