from brownie import network

ACTIVE_NETWORK = network.show_active()

OPENSEA_URL_FORMAT = "https://testnets.opensea.io/assets/{}/{}"
ETHERSCAN_IO_FORMAT = "https://{}etherscan.io/{}/{}"
