import pydriller
import os
from collections import OrderedDict
import json
import logging
with open("/media/z1xuan/blockchain_repo/repo/ethereum.json") as f:
    ethereum_repos = json.load(f)
with open("/media/z1xuan/blockchain_repo/repo/bitcoin.json") as f:
    bitcoin_repos = json.load(f)


# {repo, hash, blockchain_type, email, id, add, remove, file_changed, date}
def dump(repo, repo_name):
    try:
        for commit in pydriller.RepositoryMining(path_to_repo=repo).traverse_commits():
            commit_dict = OrderedDict()
            commit_dict["repo"] = commit.project_name
            commit_dict["hash"] = commit.hash
            bc = list()
            if repo_name in bitcoin_repos:
                bc.append("bitcoin")
            if repo_name in ethereum_repos:
                bc.append("ethereum")
            commit_dict["blockchain"] = bc
            commit_dict["email"] = commit.author.email
            commit_dict["name"] = commit.author.name
            added = 0
            removed = 0
            file_name = list()
            for m in commit.modifications:
                file_name.append(m.filename)
                added += m.added
                removed += m.removed
            commit_dict["add"] = added
            commit_dict["remove"] = removed
            commit_dict["file_changed"] = file_name
            commit_dict["date"] = str(commit.author_date)
            commit_set.append(commit_dict)
    except BaseException:
        pass


def test(repo, commit_set, num):
    try:
        for commit in pydriller.RepositoryMining(path_to_repo=repo).traverse_commits():
            num += 1
            commit_set.add(commit.hash+str(commit.author_date))
    except BaseException as e:
        print(e)
    return [commit_set, num]


commit_set = list()

if __name__ == '__main__':
    log_name = "log/commits_merge_json.log"
    logging.basicConfig(filename=log_name, filemode='a+',
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%y-%b-%d %H:%M:%S',
                        level=logging.INFO)
    for repo in bitcoin_repos:
        repo_loc = "/home/z1xuan/Desktop/repo/bitcoin/%s" % repo["dir_name"]
        dump(repo_loc, repo)
    for repo in ethereum_repos:
       if repo not in bitcoin_repos:
           repo_loc = "/home/z1xuan/Desktop/repo/ethereum/%s" % repo["dir_name"]
           dump(repo_loc, repo)

    with open("../data/blockchain.json", "w+") as f:
        json.dump(commit_set, f)