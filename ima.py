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

from skale import Skale
from skale.utils.helper import get_abi
from skale.contracts.base_contract import BaseContract, transaction_method
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import to_checksum_address

from config import ENDPOINT, ABI_FILEPATH, IMA_ABI_FILEPATH
from utils import init_wallet

init_default_logger()

DEFAULT_TOKEN_MANAGER_ADDRESS = '0x57ad607c6e90df7d7f158985c3e436007a15d744'


class LockAndData(BaseContract):
    @transaction_method
    def add_schain(self, schain_name, token_manager_address=DEFAULT_TOKEN_MANAGER_ADDRESS):
        address_fx = to_checksum_address(token_manager_address)
        return self.contract.functions.addSchain(
            schain_name,
            address_fx
        )


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
    ctx.obj['ima_abi'] = get_abi(IMA_ABI_FILEPATH)


@main.command()
@click.argument('schain_name')
@click.pass_context
def register_schain(ctx, schain_name):
    skale = ctx.obj['skale']
    ima_abi = ctx.obj['ima_abi']
    lock_and_data = LockAndData(skale, 'lock_and_data', ima_abi['lock_and_data_for_mainnet_address'], ima_abi['lock_and_data_for_mainnet_abi'])
    res = lock_and_data.add_schain(schain_name)
    print(res)


if __name__ == "__main__":
    main()
