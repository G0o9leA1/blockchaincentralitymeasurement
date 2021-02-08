import json
from .repo_crawler import GetJsonResponse

tokens = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]


def get_user_name(Id, jsp):
    url = "https://api.github.com/user/%s" % Id
    data = jsp.get_json_response(url)
    if "login" in data:
        login = data["login"]
    else:
        login = ""
    return login


def percentage(part, whole):
    # return part
    return 100 * float(part) / float(whole)


def pprint(item):
    print(json.dumps(item, indent=2))


def load():
    with open("../blockchain_with_id_selected.json") as f:
        data = json.load(f)
    return data


def get_top(data, top=-1):
    if top == -1:
        return data
    ret = dict()
    cur = 0
    for k, v in data.items():
        cur += 1
        if cur > top:
            break
        ret[k] = v
    # print(json.dumps(ret, indent=2))
    return ret


def print_all(item):
    item = {k: v for k, v in sorted(item.items(), key=lambda item: item[1], reverse=False)}
    cur = 0
    cur_val = 0
    total = len(item)
    for k, v in item.items():
        cur_val += v
        print(cur / total * 100, cur_val / 2)
        cur += 1


def print_top(item, top=50):
    headers = ['Accept: application/vnd.github.mercy-preview+json']
    jsp = GetJsonResponse(headers, tokens)
    with open("id_list.json") as f:
        id_list = json.load(f)
    cur = 0
    ret = dict()
    for k, v in item.items():
        ret[k] = round(v, 2)
        cur += 1
        if cur >= top:
            break
    for k, v in ret.items():
        print(k)
    for k, v in ret.items():
        print(v/2)
    for k, v in ret.items():
        for i, j in id_list.items():
            if int(j) == int(k):
                print(i)
                break
    for k, v in ret.items():
        for i, j in id_list.items():
            if int(j) == int(k):
                user_name = get_user_name(int(j), jsp)
                print(user_name)
                break


def analyze_single(repo_name):
    data = load()
    contrib = dict()
    total_loc = 0
    total_commit = 0
    ret = dict()
    for entry in data:
        if entry["repo"] != repo_name:
            continue
        else:
            loc = int(entry["add"]) + int(entry["remove"])
            total_commit += 1
            total_loc += loc
            if entry["id"] not in contrib:
                contrib[entry["id"]] = [0, 0]
            contrib[entry["id"]][0] += loc
            contrib[entry["id"]][1] += 1
    for Id in contrib:
        [loc, commit] = contrib[Id]
        ret[Id] = (loc / total_loc + commit / total_commit) * 100
    ret = {k: v for k, v in sorted(ret.items(), key=lambda item: item[1], reverse=True)}
    print_top(ret)
    print(len(ret))


def analyze_across(top=-1, weighted=False, commits=True, change=False, ethereum=True, bitcoin=True):
    data = load()
    contributor_dict = dict()
    ret = dict()
    with open("../data/btc_selected.json") as f:
        btc_selected = json.load(f)
    with open("../data/eth_selected.json") as f:
        eth_selected = json.load(f)
    with open("../data/ethereum_repo_raw_from_github.json") as f:
        eth_raw = json.load(f)
    with open("../data/bitcoin_repo_raw_from_github.json") as f:
        btc_raw = json.load(f)
    btc = dict()
    eth = dict()
    for entry in btc_selected:
        btc[entry] = btc_raw[entry]["forks_count"]
    for entry in eth_selected:
        eth[entry] = eth_raw[entry]["forks_count"]
    btc = get_top({k: v for k, v in sorted(btc.items(), key=lambda item: item[1], reverse=True)}, top)
    eth = get_top({k: v for k, v in sorted(eth.items(), key=lambda item: item[1], reverse=True)}, top)

    if not weighted:
        total_commit = 0
        total_loc = 0
        for entry in data:
            if bitcoin and entry["repo"] not in btc:
                continue
            if ethereum and entry["repo"] not in eth:
                continue
            if int(entry["id"]) not in contributor_dict:
                contributor_dict[int(entry["id"])] = [0, 0]

            loc = int(entry["add"]) + int(entry["remove"])
            total_commit += 1
            total_loc += loc
            if entry["id"] not in contributor_dict:
                contributor_dict[entry["id"]] = [0, 0]
            contributor_dict[entry["id"]][0] += loc
            contributor_dict[entry["id"]][1] += 1
    else:
        total_commit = 0
        total_loc = 0
        for entry in data:
            if bitcoin and entry["repo"] not in btc:
                continue
            if ethereum and entry["repo"] not in eth:
                continue
            if entry["repo"] in btc:
                weight = btc[entry["repo"]]
            else:
                weight = eth[entry["repo"]]
            if int(entry["id"]) not in contributor_dict:
                contributor_dict[int(entry["id"])] = [0, 0]

            loc = int(entry["add"]) + int(entry["remove"])
            total_commit += weight
            total_loc += loc * weight
            if entry["id"] not in contributor_dict:
                contributor_dict[entry["id"]] = [0, 0]
            contributor_dict[entry["id"]][0] += loc * weight
            contributor_dict[entry["id"]][1] += weight

    for Id in contributor_dict:
        [loc, commit] = contributor_dict[Id]
        ret[Id] = (loc / total_loc + commit / total_commit) * 100
    ret = {k: v for k, v in sorted(ret.items(), key=lambda item: item[1], reverse=True)}
    print_all(ret)


analyze_single("ethereum/go-ethereum")
# exit()
# analyze_across(top=100, weighted=False, bitcoin=True, ethereum=False, change=True, commits=True)

'''
  "bitcoin/bitcoin": 24768,
  "ccxt/ccxt": 3542,
  "askmike/gekko": 3192,
  "bbfamily/abu": 2121,
  "bitcoinj/bitcoinj": 2032
'''

'''
  "ethereum/go-ethereum": 9056,
  "ccxt/ccxt": 3542,
  "OpenZeppelin/openzeppelin-contracts": 3030,
  "ethereum/web3.js": 2688,
  "ethereum/aleth": 2214
'''
