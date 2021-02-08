import json
import itertools
from .main import preprocess_topic, parts
import os
import random
import getpass
from .utils import pprint
from .launcher import launch

# with open("files/bitcoin_raw.json") as f:
#     btc_raw = json.load(f)
#
# with open("files/btc_selected.json") as f:
#     btc_selected = json.load(f)
#
# with open("log/done.json") as f:
#     done = json.load(f)


def get_top(topic="bitcoin"):
    black_list = {"dily3825002_awesome-blockchain", "garethjns_PyBC", "zw_bitcoin-gh-meta",
                  "cancerts_study-blockchain-referrence", "willwillis_Crypto-Sentiment-Clusters",
                  "dmikushin_binance-historical-data", "johnyleebrown_cryptocurrency-research-tweets",
                  "Isaacdelly_Plutus",
                  "Zombie-3000_Bitfinex-historical-data", "protoblock_prebuiltLibs", "lukas2005_VRHackspace",
                  "philipperemy_bitcoin-market-data", "anonymousbitcoin_utxo_snapshot"}
    top_100 = dict()

    if topic == "ethereum":
        with open("files/ethereum_raw.json") as f:
            btc_raw = json.load(f)

        with open("files/eth_selected.json") as f:
            btc_selected = json.load(f)
    else:
        with open("files/bitcoin_raw.json") as f:
            btc_raw = json.load(f)

        with open("files/btc_selected.json") as f:
            btc_selected = json.load(f)
    for entry in btc_raw:
        if entry in btc_selected:
            top_100[entry] = btc_raw[entry]["stargazers_count"]

    top_100 = {k: v for k, v in sorted(top_100.items(), key=lambda item: item[1], reverse=True)}

    ele = set()
    cur = 0
    for entry in top_100:
        cur += 1
        if cur > 100:
            ele.add(entry)
    for entry in ele:
        top_100.pop(entry)

    for entry in top_100:
        if entry in black_list:
            print(entry)

    return top_100


def run(topic="bitcoin", process=5):
    username = getpass.getuser()
    [repo_data, sp_lan_dict] = preprocess_topic(topic)
    top_100 = get_top(topic)
    job_list = list()
    for repo in repo_data:
        if repo["project_name"] in top_100:
            job_list.append(repo)
    lan_list = [[], [], [], [], [], []]
    for entry in job_list:
        abs_path = "/home/%s/Desktop/repo/%s/%s" % (username, topic, entry["dir_name"])
        if abs_path in sp_lan_dict:
            lan_list[sp_lan_dict[abs_path]].append(entry)
        else:
            lan_list[-1].append(entry)
    worklist = list()
    for lan in lan_list:
        if len(lan) >=2:
            worklist += list(itertools.combinations(lan, 2))
    filtered_list = list()
    with open("eth_miss.json") as f:
        miss = json.load(f)
    for work in worklist:
        src1 = "/home/%s/Desktop/repo/%s/%s" % (username, topic, work[0]["dir_name"])
        src2 = "/home/%s/Desktop/repo/%s/%s" % (username, topic, work[1]["dir_name"])
        if [src1, src2] in miss:
            filtered_list.append(work)
    worklist = filtered_list
    random.shuffle(worklist)
    worklist = parts(worklist, process)
    with open("worklist.json", "w+") as f:
        json.dump(worklist, f)
    with open("sp_lan.json", "w+") as f:
        json.dump(sp_lan_dict, f)
    launch(topic, process)


def get_top_res(topic="bitcoin"):
    if topic == "ethereum":
        with open("log/done.json") as f:
            done = json.load(f)
    else:
        with open("log/done.json") as f:
            done = json.load(f)
    username = getpass.getuser()
    [repo_data, sp_lan_dict] = preprocess_topic(topic)
    top_100 = get_top(topic)
    job_list = list()
    for repo in repo_data:
        if repo["project_name"] in top_100:
            job_list.append(repo)
    lan_list = [[], [], [], [], [], []]
    for entry in job_list:
        abs_path = "/home/%s/Desktop/repo/%s/%s" % (username, topic, entry["dir_name"])
        if abs_path in sp_lan_dict:
            lan_list[sp_lan_dict[abs_path]].append(entry)
        else:
            lan_list[-1].append(entry)
    worklist = list()
    for lan in lan_list:
        if len(lan) >=2:
            worklist += list(itertools.combinations(lan, 2))
    filtered_list = dict()
    for work in worklist:
        src1 = "/home/%s/Desktop/repo/%s/%s" % ("lab", topic, work[0]["dir_name"])
        src2 = "/home/%s/Desktop/repo/%s/%s" % ("lab", topic, work[1]["dir_name"])
        if src1 in done and src2 in done[src1]:
            if src1.replace("/home/lab/Desktop", "/home/z1xuan/Desktop") not in filtered_list:
                filtered_list[src1.replace("/home/lab/Desktop", "/home/z1xuan/Desktop")] = dict()
            filtered_list[src1.replace("/home/lab/Desktop", "/home/z1xuan/Desktop")][src2.replace("/home/lab/Desktop", "/home/z1xuan/Desktop")] = done[src1][src2].replace("/home/lab/Desktop/clone_detector/", "/media/z1xuan/Elements/clone_detector_out/ethereum/uncompressed/")
    for entry in filtered_list:
        print(filtered_list[entry])
        break
    with open("top_100_eth_res.json", "w+") as f:
        json.dump(filtered_list, f)


def update_path(topic="bitcoin"):
    with open("top_100_btc_res.json") as f:
        data = json.load(f)
    for entry in data:
        for k, v in data[entry].items():
            data[entry][k] = v.replace("/home/z1xuan/Desktop/clone_detector/",
                                       "/media/z1xuan/Elements/clone_detector_out/bitcoin/uncompressed/")
    with open("top_100_btc_res.json", "w+") as f:
        json.dump(data, f)


def check_file(topic="bitcoin"):
    if topic == 'bitcoin':
        with open("top_100_btc_res.json") as f:
            data = json.load(f)
    else:
        with open("top_100_eth_res.json") as f:
            data = json.load(f)
    miss = list()
    for entry in data:
        for k, v in data[entry].items():
            if not os.path.exists(v):
                miss.append([entry, k])
    print(len(miss))
    if topic == 'bitcoin':
        with open("btc_miss.json", "w+") as f:
            json.dump(miss, f)
    else:
        with open("eth_miss.json", "w+") as f:
            json.dump(miss, f)


def deckard_re(topic="bitcoin"):
    if topic == "ethereum":
        with open("top_100_eth_res.json") as f:
            data = json.load(f)
    else:
        with open("top_100_btc_res.json") as f:
            data = json.load(f)
    deckard_re_list = list()
    for entry in data:
        for k, v in data[entry].items():
            src1 = entry
            src2 = k
            report_loc = v
            class_ = report_loc.strip().split('/')[-1]
            if class_ == "deckard-report.json":
                deckard_re_list.append([src1, src2])
    file_name = "btc_deckard_re.json"
    if topic == "ethereum":
        file_name = "eth_deckard_re.json"
    print(len(deckard_re_list))
    with open(file_name, "w+") as f:
        json.dump(deckard_re_list, f)


# get_top_res("ethereum")