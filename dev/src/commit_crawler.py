import json
import time
import os
import sys
import logging
from .repo_crawler import GetJsonResponse, cmd_logger

tokens = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]


def load_repo(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


# https://api.github.com/repos/ethereum/go-ethereum/commits?since=2013-12-26T13:04:45Z&page=114&per_page100
# https://api.github.com/repos/ethereum/go-ethereum/commits?since=2013-12-26T13:04:45Z&page=114&per_page=100


def generate_commit_url(repo_name, constraint, time_str,  page=1, per_page=100):
    url = "https://api.github.com/repos/%s/commits?%s%s&page=%i&per_page=%i" % (repo_name, constraint, time_str, page, per_page)
    logging.info("request url: %s " % url)
    return url


def get_modified(repo_name, sha, jsp):
    # https: // api.github.com / repos / ethereum / go - ethereum / commits / f78bd4d5d0a6198c2c0e709440d9aa370e840617
    url = "https://api.github.com/repos/%s/commits/%s" % (repo_name, sha)
    logging.info("request url: %s " % url)
    rsp = jsp.get_json_response(url)
    ret = [rsp["stats"]["total"], rsp["stats"]["additions"], rsp["stats"]["deletions"]]
    return ret


def get_commits(repo_name, created_time, jsp):
    url = generate_commit_url(repo_name, "since=", created_time)
    rsp = jsp.get_json_response(url)
    i = 1
    ret = dict()
    while len(rsp) != 0:
        i += 1
        for entry in rsp:
            if entry["commit"]["author"]["email"] not in ret:
                ret[entry["commit"]["author"]["email"]] = dict()
                ret[entry["commit"]["author"]["email"]]["commits"] = list()
            tmp = dict()
            tmp["name"] = entry["commit"]["author"]["name"]
            tmp["sha"] = entry["sha"]
            tmp["modified"], tmp["addition"], tmp["deletion"]= get_modified(repo_name, entry["sha"], jsp)
            ret[entry["commit"]["author"]["email"]]["commits"].append(tmp)
        url = generate_commit_url(repo_name, "since=", created_time, i)
        rsp = jsp.get_json_response(url)
    for entry in ret:
        ret[entry]["total"] = len(ret[entry]["commits"])
    return ret


def main(topic):
    headers = {}
    jsp = GetJsonResponse(headers, tokens)
    file_name = "repos/%s.bin" % topic
    data = load_repo(file_name)
    archive = os.listdir("commits/%s" % topic)
    log_name = "log/commits.log"
    logging.basicConfig(filename=log_name, filemode='a+',
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%y-%b-%d %H:%M:%S',
                        level=logging.INFO)
    cmd_logger()
    while len(archive) != len(data):
        try:
            for entry in data:
                file_name = entry.replace('/', '_')
                if file_name not in archive:
                    file_name = "commits/%s/" % topic + file_name
                    created = data[entry]["created_at"]
                    ret = get_commits(entry, created, jsp)
                    with open(file_name, "w+") as f:
                        json.dump(ret, f)
                    logging.info("done")
                    time.sleep(15)
        except BaseException:
            time.sleep(60)


if __name__ == "__main__":
    main(sys.argv[1])
