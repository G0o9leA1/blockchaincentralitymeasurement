import json
from .repo_crawler import GetJsonResponse
import logging
import random
import string
tokens = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]


with open("../data/bitcoin_repo_raw_from_github.json") as f:
    # load meta data download from Github
    btc_repo = json.load(f)

with open("../data/ethereum_repo_raw_from_github.json") as f:
    # load meta data download from Github
    eth_repo = json.load(f)


def random_str(n=15):
    s = ''.join(random.choices(string.digits, k=n))
    return s


def get_user_info(Id, jsp, id_list):
    url = "https://api.github.com/user/%s" % Id
    data = jsp.get_json_response(url)
    id_list[Id] = list()
    email = data["email"]
    if email != "null" and email is not None:
        id_list[Id].append(email)
    login = data["login"]
    id_list[Id].append("%s@users.noreply.github.com" % login)
    id_list[Id].append("%s+%s@users.noreply.github.com" % (Id, login))
    logging.info(login)


def get_contributors(project_name, jsp):
    i = 1
    url = "https://api.github.com/repos/%s/contributors?per_page=100&page=%i" % (project_name, i)
    data = jsp.get_json_response(url)
    contributors = list()
    while data is not None and len(data) != 0 and "message" not in data:
        for entry in data:
            contributors.append(entry["id"])
        if len(data) < 100:
            break
        i += 1
        url = "https://api.github.com/repos/%s/contributors?per_page=100&page=%i" % (project_name, i)
        data = jsp.get_json_response(url)

    return contributors


def get_id_list(id_list):
    headers = ['Accept: application/vnd.github.mercy-preview+json']
    try:
        jsp = GetJsonResponse(headers, tokens)
        for entry in btc_repo:
            contributors = get_contributors(entry, jsp)
            for contributor in contributors:
                if contributor not in id_list:
                    get_user_info(contributor, jsp, id_list)
        for entry in eth_repo:
            if entry not in btc_repo:
                contributors = get_contributors(entry, jsp)
                for contributor in contributors:
                    if contributor not in id_list:
                        get_user_info(contributor, jsp, id_list)
    except BaseException as e:
        pass
    with open("id_list.json", 'w+') as f:
        json.dump(id_list, f)


def get_id(project_name, hash, jsp):
    url = "https://api.github.com/repos/%s/commits/%s" % (project_name, hash)
    try:
        return jsp.get_json_response(url)["author"]["id"]
    except BaseException as e:
        logging.info("%s %s" %(project_name, hash))
        return None


def get_all(bc_list, id_lookup, jsp):
    for entry in bc_list:
        if entry["email"] not in id_lookup:
            Id = get_id(entry["repo"], entry["hash"], jsp)
            id_lookup[entry["email"]] = Id
            entry["id"] = Id
            logging.info(Id)
        else:
            entry["id"] = id_lookup[entry["email"]]
    return bc_list


def main():
    log_name = "log/IDs.log"
    logging.basicConfig(filename=log_name, filemode='a+',format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    headers = ['Accept: application/vnd.github.mercy-preview+json']
    jsp = GetJsonResponse(headers, tokens)
    id_list = dict()
    get_id_list(id_list)
    id_lookup = dict()
    for k, v in id_list.items():
        for entry in v:
            id_lookup[entry] = k
    with open("..data/blockchain.json") as f:
        data = json.load(f)
    bc_list = get_all(data, id_lookup, jsp)
    name_id = ["", dict()]
    for entry in bc_list:
        repo_name = entry["repo"]
        if repo_name != name_id[0]:
            name_id[1] = dict()
            name_id[0] = repo_name
        if id_lookup[entry["email"]] is not None:
            name_id[1][entry["name"]] = id_lookup[entry["email"]]
        else:
            if entry["name"] in name_id[1]:
                id_lookup[entry["email"]] = name_id[1][entry["name"]]
            else:
                id_lookup[entry["email"]] = int(random_str())
    for entry in bc_list:
        entry["id"] = int(id_lookup[entry["email"]])

    with open("..data/btc_selected.json") as f:
        # load selection
        btc_selected = json.load(f)
    with open("..data/eth_selected.json") as f:
        eth_selected = json.load(f)

    new_data = list()
    for entry in bc_list:
        if entry["repo"] in btc_selected or entry["repo"] in eth_selected:
            new_data.append(entry)

    with open("../data/blockchain_with_id_selected.json", "w+") as f:
        json.dump(new_data, f)


if __name__ == '__main__':
    main()
