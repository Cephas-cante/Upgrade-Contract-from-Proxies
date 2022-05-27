from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade


def main():
    account = get_account()
    print(f"Deploying on {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)
    # initializer = box.store, 1
    box_encoder_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoder_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )
    # Proxy code can change, but not the box address
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    # box.store(1), instead of this we would like to use the proxy
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})

    # Upgrade
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_txn = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_txn.wait(1)
    print("Proxy has been updgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
