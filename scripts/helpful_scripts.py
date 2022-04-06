from brownie import (
    accounts,
    network,
    config,
    LinkToken,
    # VRFCoordinatorMock,
    MockV3Aggregator,
    # MockOracle,
    MockDAI,
    MockWETH,
    Contract,
)
from web3 import Web3


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"  # contract address & tokenid in curly braces


BREED_MAPPING = {0: "PUG", 1: "SHIBA-INU", 2: "ST_BERNARD"}


def get_breed(breed_number):
    return BREED_MAPPING[breed_number]


def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(contract_address, amount, {"from": account})
    funding_tx.wait(1)
    print(f"Funded {contract_address}")
    return funding_tx


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockWETH,
    "weth_token": MockDAI,
    #
    "link_token": LinkToken,
    # "vrf_coordinator": VRFCoordinatorMock,
    # "oracle": MockOracle,
}

DECIMALS = 18
INITIAL_VALUE = Web3.toWei(2000, "ether")
BASE_FEE = 100000000000000000  # The premium
GAS_PRICE_LINK = 1e9  # Some value calculated depending on the Layer 1 cost and Link


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    # development context
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()

        # getting the most recent deployed mock
        contract = contract_type[-1]
    # testnets
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(DECIMALS=18, initial_value=INITIAL_VALUE):
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()

    print("Deploying mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"LinkToken deployed to {link_token.address}")

    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        DECIMALS, INITIAL_VALUE, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")

    print("Deploying Mock DAI...")
    dai_token = MockDAI.deploy({"from": account})
    print(f"Deployed to {dai_token.address}")

    print("Deploying Mock WETH...")
    weth_token = MockWETH.deploy({"from": account})
    print(f"Deployed to {weth_token.address}")
