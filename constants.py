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
from skale.utils.contracts_provision.main import _skip_evm_time

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
@click.argument('time_to_skip')
@click.pass_context
def skip_evm_time_ganache(ctx, time_to_skip):
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
@click.argument('new_dp')
@click.pass_context
def set_delegation_period(ctx, new_dp):
    """ Set delegation period (owner only transaction) """
    skale = ctx.obj['skale']
    skale.delegation_period_manager.set_delegation_period(
        months_count=int(new_dp),
        stake_multiplier=150,
        wait_for=True
    )
    print('Success')


@main.command()
@click.pass_context
def get_current_month(ctx):
    """ Get current month """
    skale = ctx.obj['skale']
    current_month = skale.time_helpers_with_debug.get_current_month()
    print(f'Current month: {current_month}')


@main.command()
@click.argument('time-to-skip')
@click.pass_context
def skip_evm_time(ctx, time_to_skip):
    """ Skip time_to_skip seconds """
    skale = ctx.obj['skale']
    skale.time_helpers_with_debug.skip_time(int(time_to_skip),
                                            wait_for=True)
    print('Success')


@main.command()
@click.argument('month_to_skip')
@click.pass_context
def skip_evm_month(ctx, month_to_skip):
    """ Skip month_to_skip months"""
    skale = ctx.obj['skale']
    time_to_skip = MONTH_IN_SECONDS * int(month_to_skip)
    skale.time_helpers_with_debug.skip_time(time_to_skip,
                                            wait_for=True)
    print('Success')


@main.command()
@click.argument('holder_address')
def get_locked_amount(ctx, holder_address):
    """ Checks quantity of freezed tokens from holder_address holder account
    """
    skale = ctx.obj['skale']
    res = skale.token_state.get_locked_amount(holder_address)
    print(res)


@main.command()
@click.pass_context
def launch_ts(ctx):
    """ Get launch timestamp
    """
    skale = ctx.obj['skale']
    res = skale.constants_holder.get_launch_timestamp()
    print(res)


@main.command()
@click.argument('launch_timestamp')
@click.pass_context
def set_launch_ts(ctx, launch_timestamp):
    """ Set launch timestamp value to launch_timestamp """
    skale = ctx.obj['skale']
    skale.constants_holder.set_launch_timestamp(int(launch_timestamp),
                                                wait_for=True)
    print('Success')


@main.command()
@click.pass_context
def disable_whitelist(ctx):
    """ Disable whitelist. Master key only transaction """
    skale = ctx.obj['skale']
    skale.validator_service.disable_whitelist(wait_for=True)
    print('Success')


@main.command()
@click.pass_context
def use_whitelist(ctx):
    """ Check if whitelist feature enabled """
    skale = ctx.obj['skale']
    print(skale.validator_service.get_use_whitelist())


if __name__ == "__main__":
    main()
