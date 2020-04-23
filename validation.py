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
""" Commands to manage SKALE validators """

import json

import click

from skale import Skale
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.web3_utils import to_checksum_address
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import private_key_to_address

from utils import init_wallet
from config import ENDPOINT, ABI_FILEPATH

from schains import create_account


init_default_logger()


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
@click.argument('name')
@click.pass_context
def register(ctx, name):
    """ Register validator """
    skale = ctx.obj['skale']
    skale.validator_service.register_validator(
        name=name,
        description='',
        fee_rate=1,
        min_delegation_amount=1,
        wait_for=True
    )


@main.command()
@click.pass_context
def ls(ctx):
    """ Show information about validators """
    skale = ctx.obj['skale']
    validators = skale.validator_service.ls()
    print(json.dumps(validators, indent=4, sort_keys=True))


@main.command()
@click.argument('validator_id')
@click.pass_context
def delegate(ctx, validator_id):
    """ Delegate tokens to validator specified by id """
    skale = ctx.obj['skale']
    msr = skale.constants_holder.msr()
    skale.delegation_service.delegate(
        validator_id=validator_id,
        amount=msr,
        delegation_period=3,
        info='',
        wait_for=True
    )


@main.command()
@click.pass_context
def delegations_by_holder(ctx):
    """ Show delegations by holder """
    skale = ctx.obj['skale']
    res = skale.delegation_controller.get_all_delegations_by_holder(
        skale.wallet.address)
    print(res)


@main.command()
@click.pass_context
def delegations_by_validator(ctx):
    """ Show delegations by validator """
    skale = ctx.obj['skale']
    res = skale.delegation_controller.get_all_delegations_by_validator(
        skale.wallet.address)
    print(res)


@main.command()
@click.argument('delegation_id')
@click.pass_context
def accept_request(ctx, delegation_id):
    """ Accept delegation specified by id """
    skale = ctx.obj['skale']
    skale.delegation_controller.accept_pending_delegation(delegation_id,
                                                          wait_for=True)


@main.command()
@click.pass_context
def send_funds(ctx):
    skale = ctx.obj['skale']
    skale_amount = 2000
    eth_amount = 3
    wallet, private_key = create_account(skale, skale_amount, eth_amount)
    print(wallet.address)
    print(private_key)


@main.command()
@click.argument('validator_id')
@click.pass_context
def whitelist(ctx, validator_id):
    """ Add validator specified by id to whitelist """
    """(owner only transaction)"""
    skale = ctx.obj['skale']
    skale.validator_service._enable_validator(int(validator_id), wait_for=True)


@main.command()
@click.argument('validator_id')
@click.pass_context
def trusted(ctx, validator_id):
    """ Check if validator specified by id trused """
    """(owner only transaction)"""
    skale = ctx.obj['skale']
    res = skale.validator_service._is_validator_trusted(int(validator_id))
    print(res)


@main.command()
@click.argument('time_to_skip')
@click.pass_context
def skip_evm_time(ctx, time_to_skip):
    """ Skip EVM time to activate delegation """
    """(works only for ganache)"""
    skale = ctx.obj['skale']
    _skip_evm_time(skale.web3, time_to_skip)
    print(f'Skipped {time_to_skip} seconds')


@main.command()
@click.argument('new_msr')
@click.pass_context
def set_msr(ctx, new_msr):
    """ Set minimum stacking amount (owner only transaction) """
    skale = ctx.obj['skale']
    skale.constants_holder._set_msr(
        new_msr=int(new_msr),
        wait_for=True
    )


@main.command()
@click.argument('validator_id')
@click.pass_context
def linked_addresses(ctx, validator_id):
    """ Get addresses that linked to validator with provided id """
    skale = ctx.obj['skale']
    vid = int(validator_id)
    res = skale.validator_service.get_linked_addresses_by_validator_id(vid)
    print(res)


@main.command()
@click.argument('address')
@click.pass_context
def validator_id_from_address(ctx, address):
    """ Get validator id from provided address """
    skale = ctx.obj['skale']
    checksum_address = address
    res = skale.validator_service.validator_id_by_address(checksum_address)
    print(res)


@main.command()
@click.argument('validator-id')
@click.pass_context
def get_link_node_signature(ctx, validator_id):
    skale = ctx.obj['skale']
    signature = skale.validator_service.get_link_node_signature(
        int(validator_id))
    print(signature)


@main.command()
@click.argument('private_key')
@click.pass_context
def link_account_to_validator(ctx, private_key):
    """ Link address from account provided by private key to validator """
    skale = ctx.obj['skale']
    address = private_key_to_address(private_key)
    checksum_address = to_checksum_address(address)
    validator_id = skale.validator_service.validator_id_by_address(
        skale.wallet.address)
    main_wallet = skale.wallet
    wallet_for_signature = Web3Wallet(private_key, skale.web3)
    skale.wallet = wallet_for_signature
    signature = skale.validator_service.get_link_node_signature(
        validator_id=validator_id
    )
    skale.wallet = main_wallet
    skale.validator_service.link_node_address(checksum_address, signature)
    print('Linked successfully')


@main.command()
@click.argument('address')
@click.argument('signature')
@click.pass_context
def link_address_to_validator(ctx, address, signature):
    """ Link given address with validator node signature to validator """
    skale = ctx.obj['skale']
    checksum_address = to_checksum_address(address)
    skale.validator_service.link_node_address(checksum_address,
                                              signature)
    print('Linked successfully')


@main.command()
@click.argument('address')
@click.pass_context
def is_main_address(ctx, address):
    """ Check if address is main for validator """
    skale = ctx.obj['skale']
    checksum_address = to_checksum_address(address)
    print(checksum_address)
    res = skale.validator_service.is_main_address(checksum_address)
    print(res)


if __name__ == "__main__":
    main()
