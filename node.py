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
from skale.utils.helper import ip_from_bytes, init_default_logger
from skale.utils.constants import LONG_LINE
from skale.contracts.manager.nodes import NodeStatus

from skale.utils.contracts_provision.main import add_all_permissions

from utils import init_wallet, generate_random_node_data
from config import ENDPOINT, ABI_FILEPATH


init_default_logger()


def create_node(skale):
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    return skale.manager.create_node(ip, port, name, public_ip, wait_for=True)


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
        create_node(skale)


@main.command()
@click.option('--save-to', default='./schains-by-node',
              help='Directory to save full schains data by specific node')
@click.pass_context
def schains_by_node(ctx, save_to):
    """ Command that shows schains for active nodes """
    skale = ctx.obj['skale']

    schains = []
    sizes = []
    for node_id in skale.nodes.get_active_node_ids():
        node = skale.nodes.get(node_id)

        node_struct = {
            'name': node['name'],
            'ip': ip_from_bytes(node['ip']),
            'basePort': node['port'],
            'publicIP': ip_from_bytes(node['publicIP']),
        }

        schains_for_node = skale.schains.get_schains_for_node(node_id)
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
@click.option('--all-nodes', is_flag=True, default=False, help='Show all nodes')
@click.pass_context
def show(ctx, all_nodes):
    """ Command to show id name and ip of active nodes """
    skale = ctx.obj['skale']

    if all_nodes:  # todo: tmp fix, remove it later
        number_of_nodes = skale.nodes.contract.functions.getNumberOfNodes().call()
        ids = range(0, number_of_nodes)
    else:
        ids = skale.nodes.get_active_node_ids()

    nodes_data = []
    for _id in ids:
        data = skale.nodes.get(_id)
        name = data.get('name')
        ip = ip_from_bytes(data.get('ip'))
        pub_key = data['publicKey']
        port = data.get('port')
        nodes_data.append((_id, name, ip, port, pub_key, NodeStatus(data['status']).name))
    print(json.dumps(nodes_data, indent=4))
    print(f'Nodes: {len(nodes_data)}')


@main.command()
@click.argument('node-name')
@click.pass_context
def remove(ctx, node_name):
    """ Command to remove node spcified by name """
    skale = ctx.obj['skale']

    node_id = skale.nodes.node_name_to_index(node_name)
    skale.manager.node_exit(node_id, wait_for=True, gas_price=4500000000)
    # skale.manager.delete_node_by_root(node_id, wait_for=True)


@main.command()
@click.pass_context
def remove_all(ctx):
    """ Command to remove all nodes """
    skale = ctx.obj['skale']
    cnt = 0
    for nid in skale.nodes.get_active_node_ids():
        skale.manager.node_exit(nid, wait_for=True)
        cnt += 1
    print(f'Success. {cnt} nodes was removed')


@main.command()
@click.argument('address')
@click.pass_context
def all_permissions(ctx, address):
    skale = ctx.obj['skale']
    add_all_permissions(skale, address)

if __name__ == "__main__":
    main()
