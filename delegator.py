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

from config import ENDPOINT, ABI_FILEPATH
from utils import init_wallet

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
@click.argument('validator_id')
@click.argument('tokens_amount', default=None)
@click.argument('period', default=3)
@click.pass_context
def delegate(ctx, validator_id, tokens_amount, period):
    """ Delegate tokens to validator specified by id """
    skale = ctx.obj['skale']
    if tokens_amount is None:
        tokens_amount = skale.constants_holder.msr()
    skale.delegation_controller.delegate(
        validator_id=int(validator_id),
        amount=int(tokens_amount),
        delegation_period=int(period),
        info='Test delegate',
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
@click.argument('validator_id')
@click.argument('address')
def withdraw_bounty(ctx, validator_id, address):
    """ Withdraw bounty from validator_id to address """
    skale = ctx.obj['skale']
    vid = int(validator_id)
    skale.distributor.withdraw_bounty(vid, address, wait_for=True)
    print('Success')


@main.command()
@click.argument('delegation_id')
def request_undelegation(ctx, delegation_id):
    """ Request undelagation for delegation provided by delegation_id """
    skale = ctx.obj['skale']
    did = int(delegation_id)
    skale.delegation_controller.request_undelegation(did, wait_for=True)
    print('Success')


@main.command()
@click.argument('delegation-id', type=int)
@click.pass_context
def delegation_by_id(ctx, delegation_id):
    skale = ctx.obj['skale']
    print(
        skale.delegation_controller.get_delegation_full(
            delegation_id
        )
    )


if __name__ == "__main__":
    main()
