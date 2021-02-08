import json
import itertools
from .main import preprocess_topic, parts
import os
import random
import getpass

black_list = {"dily3825002_awesome-blockchain", "garethjns_PyBC", "zw_bitcoin-gh-meta",
              "cancerts_study-blockchain-referrence", "willwillis_Crypto-Sentiment-Clusters",
              "dmikushin_binance-historical-data", "johnyleebrown_cryptocurrency-research-tweets", "Isaacdelly_Plutus",
              "Zombie-3000_Bitfinex-historical-data", "protoblock_prebuiltLibs", "lukas2005_VRHackspace" ,
              "philipperemy_bitcoin-market-data", "anonymousbitcoin_utxo_snapshot"}


def launch(topic, process):
    for i in range(process):
        worklist = "worklist.json"
        process_num = i
        username = getpass.getuser()
        os.system("python3.6 main.py %s %s %i %s &" %(topic, worklist, process_num, username))


def run(topic="bitcoin", num=6, process=5):
    username = getpass.getuser()
    [repo_data, sp_lan_dict] = preprocess_topic(topic)
    if num == -1:
        job_list = repo_data
    else:
        job_list = repo_data[:num]
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
    with open("log/done.json") as f:
        done = json.load(f)
    filtered_list = list()
    for work in worklist:
        if work[0]["project_name"] in black_list or work[1]["project_name"] in black_list:
            continue
        src1 = "/home/%s/Desktop/repo/%s/%s" % (username, topic, work[0]["dir_name"])
        src2 = "/home/%s/Desktop/repo/%s/%s" % (username, topic, work[1]["dir_name"])
        if src1 in done and src2 in done[src1]:
            continue
        else:
            filtered_list.append(work)
    worklist = filtered_list
    random.shuffle(worklist)
    worklist = parts(worklist, process)
    with open("worklist.json", "w+") as f:
        json.dump(worklist, f)
    with open("sp_lan.json", "w+") as f:
        json.dump(sp_lan_dict, f)
    launch(topic, process)

