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

import random
import string

from skale.wallets import LedgerWallet, RPCWallet, Web3Wallet
from skale.utils.web3_utils import init_web3

from config import ETH_PRIVATE_KEY, LEDGER, TM_URL
from skale.utils.account_tools import (check_ether_balance,
                                       check_skale_balance, generate_account,
                                       send_ether, send_tokens)


def init_wallet(endpoint):
    if TM_URL:
        return RPCWallet(TM_URL)
    web3 = init_web3(endpoint)
    if LEDGER:
        return LedgerWallet(web3, address_index=1, debug=True)
    if ETH_PRIVATE_KEY:
        return Web3Wallet(ETH_PRIVATE_KEY, web3)

        raise Exception(
            'You should provide TM_URL or ETH_PRIVATE_KEY or '
            'set LEDGER=1 to init wallet'
        )
    return Web3Wallet(ETH_PRIVATE_KEY, web3)


def generate_random_ip():
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(len=8):
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=len))


def generate_random_port():
    return random.randint(0, 60000)


def generate_random_node_data():
    return generate_random_ip(), generate_random_ip(), \
        generate_random_port(), generate_random_name()


def generate_random_schain_data():
    lifetime_seconds = 3600  # 1 hour
    type_of_nodes = 4
    return type_of_nodes, lifetime_seconds, generate_random_name()


def create_account(skale, skale_amount, eth_amount, debug=True):
    base_wallet = Web3Wallet(ETH_PRIVATE_KEY, skale.web3)
    wallet_dict = generate_account(skale.web3)
    wallet = Web3Wallet(wallet_dict['private_key'], skale.web3)

    send_tokens(skale, base_wallet, wallet.address, skale_amount, debug)
    send_ether(skale.web3, base_wallet, wallet.address, eth_amount, debug)

    if debug:
        check_ether_balance(skale.web3, wallet.address)
        check_skale_balance(skale, wallet.address)
    return wallet, wallet_dict['private_key']
