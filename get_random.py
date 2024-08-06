"""
This script will poll the blockchain.info API for the next block and extract
the last 8 characters of the hash to be used as the deterministic seed.

Nobody can predict the hash of the next block, so this is a good source of
randomness for our purposes.

Everybody can see the hash of all blocks, so this is verifiable by anyone.

Script can take some time to run (up to 10 minutes) as it waits for the next block.
"""

from datetime import datetime
import requests
import time


def get_latest_block():
    url = "https://blockchain.info/latestblock"
    response = requests.get(url)
    response.raise_for_status()
    block = response.json()

    return {
        "hash": block["hash"],
        "time": datetime.utcfromtimestamp(block["time"]),
        "index": block["block_index"]
    }


if __name__ == "__main__":

    current = get_latest_block()

    print(f"Current block: {current['index']} at {current['time']}. Waiting for new block...")
    while True:
        print(".", end="", flush=True)
        time.sleep(10)  # Check every 10 seconds
        new_block = get_latest_block()
        if new_block['index'] > current['index']:
            print(f"New block found! {new_block['index']} at {new_block['time']}")

            hash = new_block["hash"]
            # grab last 8 characters of the hash and convert to int
            last_six = int(hash[-8:], 16)
            print(f"Deterministic seed: {last_six}")
