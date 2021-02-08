import json
from .repo_crawler import GetJsonResponse
import logging
import time
with open("repos/ethereum.json") as f:
    ethereum_repo = json.load(f)

with open("eth_selected.json") as f:
    ethereum_repo_selected = json.load(f)

for k, v in ethereum_repo.items():
    if k in ethereum_repo_selected:
        print(k, v["homepage"])