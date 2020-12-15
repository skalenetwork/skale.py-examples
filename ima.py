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
""" Commands to manage SKALE IMA """

import click

from skale import Skale, SkaleIma
from skale.utils.helper import get_abi
from skale.contracts.base_contract import BaseContract, transaction_method
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import to_checksum_address

from config import ENDPOINT, ABI_FILEPATH, IMA_ABI_FILEPATH
from utils import init_wallet

init_default_logger()


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='Skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, type=click.Path(),
              help='ABI file')
@click.option('--ima-abi-filepath', default=IMA_ABI_FILEPATH, type=click.Path(),
              help='IMA ABI file')
@click.pass_context
def main(ctx, endpoint, abi_filepath, ima_abi_filepath):
    ctx.ensure_object(dict)
    wallet = init_wallet(endpoint)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath, wallet)
    ctx.obj['skale_ima'] = SkaleIma(endpoint, ima_abi_filepath, wallet)


@main.command()
@click.argument('schain_name')
@click.option('--skip-dry-run', is_flag=True, default=False)
@click.pass_context
def register_schain(ctx, schain_name, skip_dry_run):
    skale = ctx.obj['skale']
    skale_ima = ctx.obj['skale_ima']
    res = skale_ima.lock_and_data_for_mainnet.add_schain(schain_name)
    print(res)


if __name__ == "__main__":
    main()
