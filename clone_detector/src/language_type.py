import json
import os
import logging
from .utils import pprint, listdir
import getpass


def load(topic):
    with open("/home/z1xuan/Desktop/eth_dev/%s.json" % topic) as f:
        data = json.load(f)
    return data


def load_format():
    with open('formats_lookup.json') as f:
        data = json.load(f)
    return data


def get_lan_repo_list(topic, lan):
    username = getpass.getuser()
    lan_list = set()
    with open("files/%s_raw.json" % topic) as f:
        data = json.load(f)
    with open("%s.json" % topic) as f:
        dir_data = json.load(f)
    for entry in data:
        if data[entry]["language"] == lan:
            lan_list.add("/home/%s/Desktop/repo/%s/%s" % (username, topic, dir_data[entry]["dir_name"]))
    return lan_list


def get_file_language(src, look_up=load_format()):
    src = os.path.abspath(src)
    lan_dict = dict()
    lan_dict["identified"] = dict()
    lan_dict["unidentified"] = list()
    file_list = listdir(src)
    for file_name in file_list:
        ext = os.path.splitext(file_name)[1]
        if ext[1:].lower() in look_up:
            if look_up[ext[1:].lower()][0] not in lan_dict["identified"]:
                lan_dict["identified"][look_up[ext[1:].lower()][0]] = list()
            lan_dict["identified"][look_up[ext[1:].lower()][0]].append(file_name)
        else:
            lan_dict["unidentified"].append(file_name)
    return lan_dict


def analyze(topic):
    data = load(topic)
    lan_dict = dict()
    look_up = load_format()
    for entry in data:
        project_name = entry["project_name"]
        src = "/home/z1xuan/Desktop/repo/%s/%s" % (topic, entry["dir_name"])
        lan_dict[project_name] = get_file_language(src, look_up)
    return lan_dict


def main():
    log_name = "log/language.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)

    pprint(get_file_language("here"))


# lan_dict = {
#     "bitcoin": analyze("bitcoin"),
#     "ethereum": analyze("ethereum")
# }
# unidentified = dict()
# with open("language.json") as f:
#    data = json.load(f)
# for entry in data["bitcoin"]:
#     for file_name in data["bitcoin"][entry]["unidentified"]:
#         ext = os.path.splitext(file_name)[1][1:]
#         if ext not in unidentified:
#             unidentified[ext] = 0
#         unidentified[ext] += 1
# unidentified = OrderedDict(sorted(unidentified.items(), key=lambda d: d[1], reverse=True))
# pprint(unidentified)



