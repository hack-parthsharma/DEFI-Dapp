from scripts.utils import ACTIVE_NETWORK, deploy_contract, get_account, get_contract
from scripts.update_front_end import main as update_front_end

from web3 import Web3
from brownie import config

from brownie import DappToken, TokenFarm

RESERVED_BALANCE = Web3.toWei(100, "ether")


def deploy_token_and_farm(update_frontend=False, account=None, active_network=ACTIVE_NETWORK):
    if account is None:
        account = get_account()

    dapp_token = deploy_contract(
        DappToken,
        account=account
    )

    token_farm = deploy_contract(
        TokenFarm,
        account=account,
        contract_args=[
            dapp_token.address,
        ],
        publish_source=config["networks"][active_network].get("verify", False),
    )

    transfer_funds(
        dapp_token,
        token_farm,
        account=account,
        reserved=RESERVED_BALANCE,
    )

    fau_token = get_contract("fau_token", active_network=active_network)
    weth_token = get_contract("weth_token", active_network=active_network)

    allowed_tokens = {
        dapp_token: get_contract("dai_usd_pricefeed", active_network=active_network),
        fau_token: get_contract("dai_usd_pricefeed", active_network=active_network),
        weth_token: get_contract("eth_usd_pricefeed", active_network=active_network),
    }

    add_allowed_tokens(
        token_farm,
        allowed_tokens,
        account=account
    )

    if update_frontend:
        update_front_end()

    return token_farm, dapp_token


def add_allowed_tokens(token_farm, allowed_tokens: dict, account=None):
    if account is None:
        account = get_account()

    for token, pricefeed in allowed_tokens.items():
        token_farm.addAllowedToken(
            token.address,
            {
                "from": account,
            },
        ).wait(1)

        token_farm.setPriceFeedContract(
            token.address,
            pricefeed,
            {
                "from": account,
            },
        ).wait(1)


def transfer_funds(dapp_token, token_farm, account=None, reserved=RESERVED_BALANCE):
    if account is None:
        account = get_account()

    dapp_token.transfer(
        token_farm.address,
        dapp_token.totalSupply() - reserved,
        {
            "from": account,
        },
    ).wait(1)


def main():
    deploy_token_and_farm(update_frontend=True)
