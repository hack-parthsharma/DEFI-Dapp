import json

import yaml

CONTRACTS = {
    "DappToken",
    "TokenFarm",
    "MockERC20",
}


def export_config(brownie_config="./brownie-config.yaml", typescript_src="./front-end-ui/src/brownie-config.json"):
    with open(brownie_config, "r") as brownie_config_yaml, open(typescript_src, "w+") as brownie_config_json:
        json.dump(
            yaml.load(
                brownie_config_yaml,
                Loader=yaml.FullLoader,
            ),
            brownie_config_json,
            indent=4,
        )


def copy_json(src_file, dest_file, **json_kwargs):
    json.dump(
        json.load(
            src_file,
        ),
        dest_file,
        **json_kwargs
    )


def copy_deployments(deployment_map_file="./build/deployments/map.json", front_end_src="./front-end-ui/src/deployments/deployments.json"):
    with open(deployment_map_file, "r") as deployments, open(front_end_src, "w+") as front_end_deployment:
        # You can easily copy the values using front_end_deployment.write(deployments.read()) but that does not check the validity of the json formatting
        copy_json(
            src_file=deployments,
            dest_file=front_end_deployment,
            indent=4,
        )


ABI_PATH_FORMAT = "./build/contracts/{}.json"
FRONT_END_ABI_FORMAT = "./front-end-ui/src/hooks/abi/{}.json"


def copy_abi(src_abi, destination):
    with open(src_abi, "r") as src_abi_file, open(destination, "w+") as destination_abi_file:
        copy_json(
            src_file=src_abi_file,
            dest_file=destination_abi_file,
            indent=4,
        )


def main():
    export_config()
    copy_deployments()

    for contract_name in CONTRACTS:
        copy_abi(
            ABI_PATH_FORMAT.format(contract_name),
            FRONT_END_ABI_FORMAT.format(contract_name)
        )

    print("Updated front end!")
