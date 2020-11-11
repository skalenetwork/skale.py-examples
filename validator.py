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
from skale.utils.web3_utils import to_checksum_address
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import private_key_to_address
from web3 import Web3

from config import ENDPOINT, ABI_FILEPATH
from utils import init_wallet

MONTH_IN_SECONDS = (60 * 60 * 24 * 31) + 100

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
@click.pass_context
def delegations_by_validator(ctx):
    """ Show delegations by validator """
    skale = ctx.obj['skale']
    vid = skale.validator_service.validator_id_by_address(
        skale.wallet.address)
    res = skale.delegation_controller.get_all_delegations_by_validator(vid)
    print(res)


@main.command()
@click.argument('delegation_id')
@click.pass_context
def accept_request(ctx, delegation_id):
    """ Accept delegation specified by id """
    skale = ctx.obj['skale']
    delegation_id = int(delegation_id)
    skale.delegation_controller.accept_pending_delegation(delegation_id,
                                                          wait_for=True)


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
    res = skale.validator_service._is_authorized_validator(int(validator_id))
    print(res)


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
@click.argument('validator_id')
@click.pass_context
def validator_info(ctx, validator_id):
    """ Get validator info from id """
    skale = ctx.obj['skale']
    res = skale.validator_service.get(int(validator_id))
    print(json.dumps(res, indent=4))


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
    print(signature)
    skale.wallet = main_wallet
    skale.validator_service.link_node_address(checksum_address, signature,
                                              wait_for=True)
    print('Linked successfully')


@main.command()
@click.argument('validator_id')
@click.pass_context
def sign_validator_id(ctx, validator_id):
    """ Get validator_id signed by web3 wallet """
    skale = ctx.obj['skale']
    validator_id = int(validator_id)
    unsigned_hash = Web3.soliditySha3(['uint256'], [validator_id])
    print(f'Hash in bytes {unsigned_hash}')
    print(f'Vid - Unsinged hash: {validator_id} - {unsigned_hash.hex()}')
    signed_data = skale.wallet.sign_hash(unsigned_hash.hex())
    from eth_account._utils import signing
    v = signed_data.v
    print(f'v in bytes: {signing.to_bytes(v)}')
    print(f'v in hex: {signing.to_bytes(v).hex()}')
    print(signed_data)
    print(signed_data.signature)
    print(signed_data.signature.hex())


@main.command()
@click.argument('address')
@click.argument('signature')
@click.pass_context
def link_address_to_validator(ctx, address, signature):
    """ Link given address with validator node signature to validator """
    skale = ctx.obj['skale']
    checksum_address = to_checksum_address(address)
    # signature = signature.strip()
    # signature = HexBytes(signature).hex()
    vid = skale.validator_service.validator_id_by_address(skale.wallet.address)
    print(vid)
    print(checksum_address)
    print(signature)
    skale.validator_service.link_node_address(checksum_address,
                                              signature,
                                              wait_for=True)
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


@main.command()
@click.pass_context
def trusted_ids(ctx):
    """ Get trusted validators ids list """
    skale = ctx.obj['skale']
    print(skale.validator_service.get_trusted_validator_ids())


@main.command()
@click.argument('validator-id', type=int)
@click.pass_context
def delegations_by_validator_id(ctx, validator_id):
    skale = ctx.obj['skale']
    print(
        skale.delegation_controller._get_delegation_ids_by_validator(
            validator_id)
    )


if __name__ == "__main__":
    main()
