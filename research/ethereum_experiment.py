from src.blockchain.client import EthereumClient


def main():

    client = EthereumClient()

    latest = client.latest_block()

    print("=" * 60)
    print("ETHEREUM BLOCK")
    print("=" * 60)

    print(f"Block number: {latest}")

    block = client.get_block(latest)

    print(f"Timestamp:    {block['timestamp']}")
    print(f"Transactions: {len(block['transactions'])}")

    print("\nTRANSACTIONS")
    print("-" * 60)

    for tx in block["transactions"][:10]:

        print(f"Hash:  {tx['hash'].hex()}")
        print(f"From:  {tx['from']}")
        print(f"To:    {tx['to']}")
        print(
            f"Value: {client.w3.from_wei(tx['value'], 'ether')} ETH"
        )
        print("-" * 60)


if __name__ == "__main__":
    main()