from src.blockchain.client import EthereumClient


def main():

    client = EthereumClient()

    block_number = client.latest_block()

    print(f"Latest Ethereum block: {block_number}")


if __name__ == "__main__":
    main()