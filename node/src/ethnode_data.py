import json
import time
import urllib.request
import urllib.error
import logging
import subprocess
import os


def cmd_logger():
    cmd = "ps -p %i -o args | grep python" % os.getpid()
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    logging.info(subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True).stdout)


def getUrl(start, length, timestamp=int(time.time()*1000)):
    url = "https://ethernodes.org/data?draw=1&columns%5B0%5D%5Bdata%5D=id&columns%5B0%5D%5Bname%5D=&columns%5B0%5D" \
          "%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=host&columns%5B1%5D%5Bname%5D=&columns%5B1%5D" \
          "%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=isp&columns%5B2%5D%5Bname%5D=&columns%5B2%5D" \
          "%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=country&columns%5B3%5D%5Bname%5D=&columns%5B3%5D" \
          "%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=client&columns%5B4%5D%5Bname%5D=&columns%5B4%5D" \
          "%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=clientVersion&columns%5B5%5D%5Bname%5D=&columns%5B5%5D" \
          "%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=os&columns%5B6%5D%5Bname%5D=&columns%5B6%5D" \
          "%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=lastUpdate&columns%5B7%5D%5Bname%5D=&columns%5B7%5D" \
          "%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=inSync&columns%5B8%5D%5Bname%5D=&columns%5B8%5D" \
          "%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D" \
          "%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=" + str(start) + \
          "&length=" + str(length) + "&search%5Bvalue%5D=&search%5Bregex%5D=false&_=" + str(timestamp)
    return url


def fetch_records_total():
    url = getUrl(0, 1)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    f = urllib.request.urlopen(urllib.request.Request(url=url, headers=headers))
    data = f.read()
    encoding = f.info().get_content_charset('utf-8')
    JSON_object = json.loads(data.decode(encoding))
    return JSON_object["recordsTotal"]


def download_all():
    length = fetch_records_total()
    start = 0
    timestamp = int(time.time() * 1000)
    url = getUrl(start, length)
    logging.info(timestamp)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    f = urllib.request.urlopen(urllib.request.Request(url=url, headers=headers))
    data = f.read()
    encoding = f.info().get_content_charset('utf-8')
    JSON_object = json.loads(data.decode(encoding))
    with open("tmp/" + str(timestamp) + ".json", 'w+') as f:
        json.dump(JSON_object, f)
    return timestamp


def gen_id_ip():
    id2ip = dict()
    with open("data/ethnode_org_data") as f:
        data = json.load(f)["data"]
        for entry in data:
            if entry['id'] not in id2ip:
                id2ip[entry["id"]] = list()
                id2ip[entry["id"]].append(entry["host"])
            elif entry["host"] not in id2ip[entry["id"]]:
                id2ip[entry["id"]].append(entry["host"])

    with open("data/id_host_data", 'w') as f:
        json.dump(id2ip, f)
    print(json.dumps(id2ip, indent=4))


def merge(file_name):
    with open(file_name, 'r') as f:
        tmp_json = json.load(f)['data']
    with open('data/ethnode_org_data') as f:
        org_data = json.load(f)
    with open('data/id_host_data') as f:
        id_host = json.load(f)

    for entry in tmp_json:
        if entry['id'] not in id_host:
            id_host[entry['id']] = list()
            id_host[entry['id']].append(entry['host'])
            org_data["data"].append(entry)
        elif entry["host"] not in id_host[entry["id"]]:
            id_host[entry["id"]].append(entry["host"])
    length = 0
    for entry in id_host:
        length += len(id_host[entry])
    logging.info(length)
    org_data["recordsTotal"] = len(id_host)
    org_data["update_time"] = file_name.replace("tmp/", '').split('.')[0]
    with open('data/ethnode_org_data', 'w+') as f:
        json.dump(org_data, f)
    with open('data/id_host_data', 'w+') as f:
        json.dump(id_host, f)


def update():
    file_name = "tmp/" + str(download_all()) + '.json'
    merge(file_name)


def update_per_time(interval=86400):
    while 1:
        try:
            update()
        except urllib.error.URLError:
            logging.critical("error!")
        time.sleep(interval)


if __name__ == "__main__":
    log_name = "log/ethnode_data.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    cmd_logger()
    update_per_time()
