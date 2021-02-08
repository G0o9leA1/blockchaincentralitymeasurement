import json
import math
from collections import OrderedDict
import time
import numpy as np
import sys
import logging
import os
import subprocess
import pycurl
from io import BytesIO

tokens = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]


class GetJsonResponse:
    def __init__(self, headers, tokens):
        self.headers = headers
        self.tokens = tokens
        self.cur_token = 0
        self.token_num = len(tokens)
        self.pycurl_connect = pycurl.Curl()

    def get_json_response(self, url):
        token_obj = 'token %s' % self.tokens[self.cur_token]
        if 'Authorization' in self.headers[-1]:
            if 'Authorization: %s' % token_obj != self.headers[-1]:
                self.headers[-1] = 'Authorization: %s' % token_obj
        else:
            self.headers.append('Authorization: %s' % token_obj)
        self.pycurl_connect.setopt(pycurl.HTTPHEADER, self.headers)
        self.pycurl_connect.setopt(pycurl.URL, url)
        data = BytesIO()
        self.pycurl_connect.setopt(pycurl.WRITEFUNCTION, data.write)
        self.pycurl_connect.perform()
        status_code = self.pycurl_connect.getinfo(pycurl.RESPONSE_CODE)
        data = data.getvalue().decode('utf-8')
        if status_code == 403:
            while self.check_limit(self.tokens[self.cur_token]) == 0:
                if self.token_num > self.cur_token + 1:
                    self.cur_token += 1
                else:
                    self.cur_token = 0
                    while self.check_all() == 0:
                        time.sleep(30)
            return self.get_json_response(url)
        else:
            return json.loads(data, object_pairs_hook=OrderedDict)

    def check_limit(self, token):
        url = "https://api.github.com/rate_limit"
        token_obj = 'token %s' % token
        headers = ['Authorization: %s' % token_obj]
        pycurl_connect = pycurl.Curl()
        pycurl_connect.setopt(pycurl.HTTPHEADER, headers)
        pycurl_connect.setopt(pycurl.URL, url)
        data = BytesIO()
        pycurl_connect.setopt(pycurl.WRITEFUNCTION, data.write)
        pycurl_connect.perform()
        data = json.loads(data.getvalue().decode('utf-8'), object_pairs_hook=OrderedDict)
        return data["rate"]["remaining"]

    def check_all(self):
        ret = 0
        for token in self.tokens:
            ret += self.check_limit(token)
        return ret


def getTimeAvg(timestamp1, timestamp2):
    dates = [timestamp1, timestamp2]
    mean = (np.array(dates, dtype='datetime64[s]')
            .view('i8')
            .mean()
            .astype('datetime64[s]'))

    return "%sZ" % mean


def generate_topic_time_window_url(topic, timestamp1, timestamp2):
    url = "https://api.github.com/search/repositories?q=topic:%s+created:%s..%s" %(topic, timestamp1, timestamp2)
    return url


def gen_window_total(topic, timestamp1, timestamp2, jsp):
    url = generate_topic_time_window_url(topic, timestamp1, timestamp2)
    rsp = jsp.get_json_response(url)
    return [rsp["total_count"], url]


def gen_query_list(topic, time_list, index, jsp, query_list):
    if index < len(time_list)-1:
        num, url = gen_window_total(topic, time_list[index], time_list[index+1], jsp)
        while num > 1000:
            mid = getTimeAvg(time_list[index], time_list[index+1])
            time_list.insert(index+1, mid)
            num, url = gen_window_total(topic, time_list[index], time_list[index + 1], jsp)
        logging.info("Time Window %i: %s - %s" % (index+1,  time_list[index], time_list[index+1]))
        query_list.append(url)
        return gen_query_list(topic, time_list, index+1, jsp, query_list)
    else:
        return query_list


def download_per_query(query, jsp, update=False):
    if update:
        logging.disable(logging.CRITICAL)
    url = "%s&page=%i&per_page=%i" %(query, 1, 100)
    rsp = jsp.get_json_response(url)
    ret = dict()
    logging.info("request url: %s" % url)
    logging.info("total_count: %s" % rsp["total_count"])
    request_time = math.ceil((rsp["total_count"]) / 100)
    logging.info("total_request_time %s" % request_time)
    i = 1
    while i <= request_time:
        for entry in rsp["items"]:
            if entry["full_name"] in ret:
                logging.warning(entry["full_name"])
            else:
                ret[entry["full_name"]] = entry
                logging.info("Append %s" % entry["full_name"])
        i += 1
        url = "%s&page=%i&per_page=%i" %(query, i, 100)
        logging.info("request url: %s " % url)
        rsp = jsp.get_json_response(url)
    if update:
        logging.disable(logging.NOTSET)
    return ret


def download_by_time_topic(topic, time_list, file_name, jsp, update=False):
    if not update:
        logging.info("Generating Time List")
        query_list = gen_query_list(topic, time_list, 0, jsp, [])
        logging.info("Generating Query List")
        for index in range(len(query_list)):
            logging.info("Query %i: %s" % (index + 1, query_list[index]))
    else:
        logging.info("Using Old Query List")
        query_list = time_list
    if not update:
        data = dict()
        for query in query_list:
            data.update(download_per_query(query, jsp))
    else:
        with open(file_name) as f:
            data = json.load(f)
        for query in query_list:
            downloaded = download_per_query(query, jsp, update)
            for entry in downloaded:
                if entry not in data:
                    data[entry] = downloaded[entry]
                    logging.info("Append %s" % entry)
    with open(file_name, "w+") as f:
        json.dump(data, f)
    return query_list


def verify(download_length, topic, time_list, jsp):
    total = gen_window_total(topic, time_list[0], time_list[1], jsp)[0]
    if total == download_length:
        return True
    logging.info("have %i in total" % total)
    logging.info("downloaded %i " % download_length)
    return False


def cmd_logger():
    cmd = "ps -p %i -o args | grep python" % os.getpid()
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    logging.info(subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True).stdout)


def main(topic, start, end):
    file_name = "repos/%s.json" % topic
    log_name = "log/repos.log"
    logging.basicConfig(filename=log_name, filemode='a+',format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    headers = ['Accept: application/vnd.github.mercy-preview+json']
    jsp = GetJsonResponse(headers, tokens)
    time_list = [start, end]
    query_list = download_by_time_topic(topic, time_list, file_name, jsp)
    with open(file_name) as f:
        data = json.load(f)
    verified = verify(len(data), topic, [start, end], jsp)
    logging.info("Fully Collected? %r" % verified)
    while not verified:
        download_by_time_topic(topic, query_list, file_name, jsp, update=True)
        with open(file_name) as f:
            data = json.load(f)
        verified = verify(len(data), topic, [start, end], jsp)
        logging.info("Fully Collected? %r" % verified)
    logging.info("Done!")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python repo_crawler.py topic start_time end_time")
        exit(0)
    topic = sys.argv[1]
    start = "%sT00:00:00Z" % sys.argv[2]
    end = "%sT00:00:00Z" % sys.argv[3]
    main(topic, start, end)


