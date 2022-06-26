import pytest
from scripts import ACTIVE_NETWORK
from scripts.deploy import deploy_token_and_farm
from scripts.utils import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract

from web3 import Web3
from brownie import network, exceptions

from brownie import DappToken, TokenFarm

DECIMALS = 18
INITIAL_VALUE = 2000000000000000000000

KEPT_BALANCE = Web3.toWei(100, "ether")


def test_set_price_feed():
    """The owner address should be the only address allowed to set a price feed contract address
    """
    ACTIVE_NETWORK = network.show_active()

    if ACTIVE_NETWORK not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip(f"Only for local testing, currently on {ACTIVE_NETWORK}")

    account = get_account()
    non_owner = get_account(index=1)

    token_farm, dapp_token = deploy_token_and_farm(
        account=account,
        active_network=ACTIVE_NETWORK,
    )

    token_farm.setPriceFeedContract(
        dapp_token.address,
        get_contract("eth_usd_pricefeed", active_network=ACTIVE_NETWORK),
        {
            "from": account,
        },
    ).wait(1)

    assert token_farm.tokenPriceFeed(dapp_token.address) == get_contract("eth_usd_pricefeed", active_network=ACTIVE_NETWORK), \
        "Pricefeed contracts do not match!"

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address,
            get_contract("fau_token", active_network=ACTIVE_NETWORK),
            {
                "from": non_owner,
            },
        ).wait(1)

    assert token_farm.tokenPriceFeed(dapp_token.address) != get_contract("fau_token", active_network=ACTIVE_NETWORK), \
        "Any account can override the pricefeed!"


def test_stake_tokens(amount_staked):
    ACTIVE_NETWORK = network.show_active()

    if ACTIVE_NETWORK not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip(f"Only for local testing, currently on {ACTIVE_NETWORK}")

    account = get_account()

    token_farm, dapp_token = deploy_token_and_farm(
        account=account,
        active_network=ACTIVE_NETWORK,
    )

    dapp_token.approve(
        token_farm.address,
        amount_staked,
        {
            "from": account,
        },
    ).wait(1)

    token_farm.stakeToken(
        dapp_token.address,
        amount_staked,
        {
            "from": account,
        },
    ).wait(1)

    staking_balance = token_farm.stakingBalance(
        dapp_token.address,
        account.address,
    )

    assert staking_balance == amount_staked, "Staking balance does not match amount staked"

    unique_tokens_staked = token_farm.uniqueTokensStaked(account.address)
    assert unique_tokens_staked == 1, f"Invalid amount of unique tokens: {unique_tokens_staked}"

    first_staker = token_farm.stakers(0)
    assert first_staker == account.address, f"Staker address at index 0 is invalid: {first_staker}"

    return token_farm, dapp_token, account


def test_issue_tokens(amount_staked):
    ACTIVE_NETWORK = network.show_active()

    if ACTIVE_NETWORK not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip(f"Only for local testing, currently on {ACTIVE_NETWORK}")

    token_farm, dapp_token, account = test_stake_tokens(amount_staked)

    starting_balance = dapp_token.balanceOf(account.address)

    token_farm.issueTokens(
        {
            "from": account,
        },
    ).wait(1)

    new_balance = dapp_token.balanceOf(account.address)
    assert new_balance == starting_balance + INITIAL_VALUE

    return token_farm, dapp_token
