# Local packages
from scripts import ACTIVE_NETWORK, ETHERSCAN_IO_FORMAT

# Installed packages
from web3 import Web3
import eth_utils
from brownie import accounts, config, Contract, exceptions

# Variable imports, may not exist
from brownie import (
    MockWETH,
    MockV3Aggregator,
    MockDAI,
)

DECIMALS = 18
INITIAL_VALUE = 2000000000000000000000

MOCK_CONTRACTS = {
    "eth_usd_pricefeed": MockV3Aggregator,
    "dai_usd_pricefeed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = {
    "development",
    "ganache-local",
}

LOCAL_BLOCKCHAIN_ENVIRONMENTS = {
    *NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    "mainnet-fork",
    "mainnet-fork-dev",
    "binance-fork",
    "matic-fork",
}

FORKED_LOCAL_ENVIRONMENTS = {
    "mainnet-fork",
    "mainnet-fork-dev",
}

ALL_LOCAL_BLOCKCHAIN_ENVIRONMENTS = {
    *LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    *FORKED_LOCAL_ENVIRONMENTS,
}


def get_config(*path, default_value=None):
    value = config
    try:
        for route in path:
            value = value[route]
    except KeyError:
        return default_value
    return value


def get_account(index: int = None, account_id=None, active_network=ACTIVE_NETWORK):
    if index is not None:
        return accounts[index]
    elif account_id is not None:
        return accounts.load(account_id)

    if active_network in (NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS | FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    elif active_network is None:
        return accounts[0]

    return accounts.add(
        get_config("wallets", "private_key")
    )


def deploy_contract(contract,  contract_args=[], account=None, publish_source=False, **account_kwargs):
    if account is None:
        account = get_account()
    return contract.deploy(
        *contract_args,
        {
            "from": account,
            **account_kwargs,
        },
        publish_source=publish_source,
    )


def get_contract(contract_name, active_network=ACTIVE_NETWORK):
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it

        Args:
            contract_name (string): This is the name that is refered to in the
            brownie config and 'contract_to_mock' variable.

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictonary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = MOCK_CONTRACTS[contract_name]
    if active_network in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][active_network][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(
                f"{active_network} address not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run scripts/deploy_mocks.py --network {active_network}"
            )
            raise KeyError(
                f"Could not find {contract_name} on {active_network}"
            )
    return contract


def print_etherscan(address: str, transaction_type: str = None):

    if ACTIVE_NETWORK in ALL_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print("This transaction is local and will not be found on etherscan")
    else:
        subdomain = "" if "mainnet" in ACTIVE_NETWORK else f"{ACTIVE_NETWORK}."

        print(
            f"View transaction at {ETHERSCAN_IO_FORMAT.format(subdomain, transaction_type, address)}"
        )


def encode_function_data(initializer=None, *args):
    if not args or initializer is None:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade_contract(proxy_contract, new_address, account=None, proxy_admin_contract=None, initializer=None, *initializer_args):
    if proxy_admin_contract is not None:
        if initializer is not None:
            encoded_call = encode_function_data(initializer, *initializer_args)

            transaction = proxy_admin_contract.upgradeAndCall(
                proxy_contract.address,
                new_address,
                encoded_call,
                {
                    "from": account,
                },
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy_contract.address,
                new_address,
                {
                    "from": account,
                },
            )
    elif initializer is not None:
        encoded_call = encode_function_data(initializer, *initializer_args)
        transaction = proxy_contract.upgradeToAndCall(
            proxy_contract.address,
            new_address,
            encoded_call,
            {
                "from": account,
            },
        )
    else:
        transaction = proxy_contract.upgradeTo(
            new_address,
            {
                "from": account,
            },
        )
    return transaction


def deploy_mocks(decimals=18, initial_value=2000000000000000000000):
    print("Deploying mocks")
    deploy_mock(
        "eth_usd_pricefeed",
        mock_contract_args=[
            decimals,
            initial_value,
        ]
    )

    deploy_mock("weth_token")

    deploy_mock("fau_token")

    print("Deployed mocks!")


def deploy_mock(mock_contract_name, mock_contract_args: list = [], mock_contract_kwargs: dict = {}, account=None):
    if account is None:
        account = get_account()

    try:
        mock_contract = MOCK_CONTRACTS[mock_contract_name]
    except KeyError:
        print(f"{mock_contract_name} is not available!")
        return

    print(f"Deploying {mock_contract_name}")
    deployed_contract = deploy_contract(
        mock_contract,
        contract_args=mock_contract_args,
        **mock_contract_kwargs,
    )
    print("Deployed!")

    return deployed_contract
