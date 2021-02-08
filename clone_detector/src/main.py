import json
import logging
from .dupl_detect import dupl
from .jscpd_detect import jscpd
from .deckard_detect import deckard
from .language_type import get_lan_repo_list
import sys


def preprocess_topic(topic):
    # [Java, C, PHP, Solidity, Go]
    lan_list = ['Java', 'C', 'PHP', 'Solidity', 'Go']
    sp_lan_list = list(map(lambda a: get_lan_repo_list(topic, a), lan_list))
    sp_lan_dict = dict()
    for i in range(5):
        for entry in sp_lan_list[i]:
            sp_lan_dict[entry] = i

    with open("files/%s.json" % topic) as f:
        repo_data = json.load(f)

    if topic == "ethereum":
        with open("files/eth_selected.json") as f:
            selected = set(json.load(f))

    else:
        with open("files/btc_selected.json") as f:
            selected = set(json.load(f))

    new_data = list()
    for entry in repo_data:
        if entry["project_name"] in selected:
            new_data.append(entry)

    return [new_data, sp_lan_dict]


def preprocess():
    bitcoin_repo_data, sp_lan_dict = preprocess_topic('bitcoin')
    ethereum_repo_data, ethereum_sp_lan_dict = preprocess_topic('ethereum')
    sp_lan_dict.update(ethereum_sp_lan_dict)
    return [bitcoin_repo_data, ethereum_repo_data, sp_lan_dict]


def diff(topic1, project_name1, src1, topic2, project_name2, src2, sp_lan_dict, language_data, username):
    if src1 == src2:
        logging.info("%s %s same source" % (src1, src2))
        return
    if project_name1 == project_name2:
        logging.info("%s %s same repository in different type" % (src1, src2))
        return

    if src1 in sp_lan_dict and src2 in sp_lan_dict:
        a = sp_lan_dict[src1]
        b = sp_lan_dict[src2]
        if a != b:
            pass
        elif a == 4:
            try:
                output_file_loc = dupl(src1, src2)
                if output_file_loc is None:
                    logging.critical("%s %s dupl %s" % (src1, src2, "engine error"))
                else:
                    logging.info("%s %s dupl %s" % (src1, src2, output_file_loc))
            except BaseException as e:
                logging.critical("%s %s dupl %s" % (src1, src2, e))
        else:
            try:
                output_file_loc = deckard(src1, src2, a)
                if output_file_loc is None:
                    logging.critical("%s %s deckard %s" % (src1, src2, "engine error"))
                else:
                    logging.info("%s %s deckard %s" % (src1, src2, output_file_loc))
            except BaseException as e:
                logging.critical("%s %s deckard %s" % (src1, src2, e))
    elif src1 not in sp_lan_dict and src2 not in sp_lan_dict:
        try:
            output_file_loc = jscpd(topic1, project_name1, src1, topic2, project_name2, src2, language_data, username)
            if output_file_loc is None:
                logging.critical("%s %s jscpd %s" % (src1, src2, "engine error"))
            else:
                logging.info("%s %s jscpd %s" % (src1, src2, output_file_loc))
        except BaseException as e:
            logging.critical("%s %s jscpd %s" % (src1, src2, e))


def parts(l, n):
    q, r = divmod(len(l), n)
    I = [q * i + min(i, r) for i in range(n + 1)]
    return [l[I[i]:I[i + 1]] for i in range(n)]


def diff_list(topic, work_list, process_num, username):
    with open(work_list) as f:
        work_list = json.load(f)[int(process_num)]
    with open("sp_lan.json") as f:
        sp_lan_dict = json.load(f)
    with open("language.json") as f:
        language_data = json.load(f)
    for entry in work_list:
        diff(topic, entry[0]["project_name"], "/home/%s/Desktop/repo/%s/%s" % (username, topic, entry[0]["dir_name"]),
             topic, entry[1]["project_name"], "/home/%s/Desktop/repo/%s/%s" % (username, topic, entry[1]["dir_name"]),
             sp_lan_dict, language_data, username)


if __name__ == "__main__":
    log_name = "log/repos.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    diff_list(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
