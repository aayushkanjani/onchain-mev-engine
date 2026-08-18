from src.blockchain.client import EthereumClient
from src.blockchain.events import decode_transfer


TX_HASH = (
    "c5568dd6836ad0ec3a6b81e457df8a52312621eb381d08e630ae581091f812ab"
)


def main():

    client = EthereumClient()

    receipt = client.get_transaction_receipt(TX_HASH)

    print("=" * 60)
    print("DECODED EVENTS")
    print("=" * 60)

    for log in receipt["logs"]:

        transfer = decode_transfer(log,decimals=6)

        if transfer is not None:

            print("\nERC-20 TRANSFER")

            print(f"From:        {transfer['from']}")
            print(f"To:          {transfer['to']}")
            print(f"Raw amount:  {transfer['raw_value']}")
            print(f"USDC amount: {transfer['value']}")


if __name__ == "__main__":
    main()