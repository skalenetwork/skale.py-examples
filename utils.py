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

from skale.wallets import RPCWallet
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3

from config import TM_URL, ETH_PRIVATE_KEY


def init_wallet(endpoint):
    if not TM_URL and not ETH_PRIVATE_KEY:
        raise Exception('You should provide TM_URL or ETH_PRIVATE_KEY to init wallet')
    if TM_URL:
        return RPCWallet(TM_URL)
    web3 = init_web3(endpoint)
    return Web3Wallet(ETH_PRIVATE_KEY, web3)


def generate_random_ip():
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(len=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=len))


def generate_random_port():
    return random.randint(0, 60000)


def generate_random_node_data():
    return generate_random_ip(), generate_random_ip(), generate_random_port(), \
        generate_random_name()


def generate_random_schain_data():
    lifetime_seconds = 3600  # 1 hour
    type_of_nodes = 4
    return type_of_nodes, lifetime_seconds, generate_random_name()
