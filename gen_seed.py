"""
The script polls https://api.drand.sh/public/latest every 1 second to check for a new randomness round
(published every 30 sec).

Since Drand’s output is produced via a decentralized, publicly verifiable process, anyone with access to the beacon’s
parameters can reproduce and verify the randomness based solely on the round’s timestamp and the procedure.
See: https://drand.love/about/#why-decentralized-randomness-is-important

When a new round is detected (i.e. its round number exceeds the previously stored one), the randomness from that
round becomes your verifiable, deterministic seed.

Randomness can be verified based on round number: https://api.drand.sh/public/{round}
"""

import requests
import time
from datetime import datetime


def get_latest_round():
    url = "https://api.drand.sh/public/latest"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data


if __name__ == "__main__":
    current = get_latest_round()
    print("Latest round")
    print(datetime.now(), current)

    while True:
        print(".", end="", flush=True)
        time.sleep(1)
        new = get_latest_round()
        if new["round"] > current["round"]:
            time_found = datetime.now()
            print("")
            print(f"{time_found} - Round found: {new}")
            print(f"# Deterministic seed (randomness as decimal integer): {int(new['randomness'], 16)}")

            current = new
            break