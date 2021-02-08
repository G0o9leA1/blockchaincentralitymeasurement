import json
import shutil
# import ghlinguist as ghl
import json
from collections import OrderedDict

with open("../data/ethereum_repo_raw_from_github.json") as f:
    ethereum_repos = json.load(f)
with open("../data/bitcoin_repo_raw_from_github.json") as f:
    bitcoin_repos = json.load(f)
with open('../data/btc_selected.json') as f:
    bitcoin_repo_selected = set(json.load(f))
with open('../data/eth_selected.json') as f:
    ethereum_repo_selected = set(json.load(f))


def language_list(topic):
    lang = dict()
    if topic == "bitcoin":
        for k, v in bitcoin_repos.items():
            if k not in bitcoin_repo_selected:
                continue
            if v["language"] not in lang:
                lang[v["language"]] = 0
            lang[v["language"]] += 1
    else:
        for k, v in ethereum_repos.items():
            if k not in ethereum_repo_selected:
                continue
            if v["language"] not in lang:
                lang[v["language"]] = 0
            lang[v["language"]] += 1
    sorted_x = sorted(lang.items(), key=lambda kv: kv[1], reverse=True)
    sorted_dict = OrderedDict(sorted_x)
    return output(topic, sorted_dict)


def output(topic, sorted_dict):
    num = 0
    for k, v in sorted_dict.items():
        num += v
    print(topic)
    print("######")
    for k, v in sorted_dict.items():
        print(k, round(v/num, 4)*100)
    print("######")


if __name__ == '__main__':
    language_list("bitcoin")
    language_list("ethereum")




