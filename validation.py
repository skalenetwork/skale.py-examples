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

import click

from skale import Skale
from skale.utils.helper import init_default_logger

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
    """ Command to remove node spcified by name """
    skale = ctx.obj['skale']
    skale.delegation_service.register_validator(
        name=name,
        description='',
        fee_rate=1,
        min_delegation_amount=1,
        wait_for=True
    )


@main.command()
@click.pass_context
def ls(ctx):
    skale = ctx.obj['skale']
    validators = skale.validator_service.ls()
    print(validators)


@main.command()
@click.argument('validator_id')
@click.pass_context
def delegate(ctx, validator_id):
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
    skale = ctx.obj['skale']
    res = skale.delegation_service.get_all_delegations_by_holder(skale.wallet.address)
    print(res)


@main.command()
@click.pass_context
def delegations_by_validator(ctx):
    skale = ctx.obj['skale']
    res = skale.delegation_service.get_all_delegations_by_validator(skale.wallet.address)
    print(res)


@main.command()
@click.argument('delegation_id')
@click.pass_context
def accept_request(ctx, delegation_id):
    skale = ctx.obj['skale']
    skale.delegation_service.accept_pending_delegation(delegation_id, wait_for=True)


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
    """Owner only transaction"""
    skale = ctx.obj['skale']
    skale.validator_service._enable_validator(validator_id, wait_for=True)


@main.command()
@click.argument('validator_id')
@click.pass_context
def trusted(ctx, validator_id):
    skale = ctx.obj['skale']
    res = skale.validator_service._is_validator_trusted(validator_id)
    print(res)


@main.command()
@click.argument('delegation_id')
@click.pass_context
def skip_delay(ctx, delegation_id):
    """Owner only transaction"""
    skale = ctx.obj['skale']
    skale.token_state._skip_transition_delay(delegation_id, wait_for=True)


@main.command()
@click.argument('new_msr')
@click.pass_context
def set_msr(ctx, new_msr):
    """Owner only transaction"""
    skale = ctx.obj['skale']
    skale.constants_holder._set_msr(
        new_msr=new_msr,
        wait_for=True
    )


if __name__ == "__main__":
    main()
