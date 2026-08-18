from web3 import Web3


TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()


def decode_transfer(log, decimals=None):

    topics = log["topics"]

    if topics[0].hex() != TRANSFER_TOPIC:
        return None

    from_address = Web3.to_checksum_address(
        "0x" + topics[1].hex()[-40:]
    )

    to_address = Web3.to_checksum_address(
        "0x" + topics[2].hex()[-40:]
    )

    raw_value = int.from_bytes(
        log["data"],
        byteorder="big",
    )

    result = {
        "from": from_address,
        "to": to_address,
        "raw_value": raw_value,
    }

    if decimals is not None:
        result["value"] = raw_value / (10 ** decimals)

    return result