import logging
import shodan
import json
import os
from .ethnode_data import cmd_logger
from .back_up import move_data_local
import time
import gzip
import shutil
import urllib.request
import urllib.error
SHODAN_API_KEY = ""


def collect(collected_file, uncollected_file):
    api = shodan.Shodan(SHODAN_API_KEY)
    data = load()
    for entry in data:
        logging.info("Downloading node: %s" % entry)
        uncollected = dict()
        collected = dict()
        for ip in data[entry]:
            ret = query_per_ip(api, ip)
            if not ret:
                if entry not in uncollected:
                    uncollected[entry] = list()
                uncollected[entry] = ip
            else:
                if entry not in collected:
                    collected[entry] = list()
                collected[entry] = ip
            time.sleep(1)
        tracker(collected_file, uncollected_file, collected, uncollected)


def tracker(collected_file, uncollected_file, collected, uncollected):
    old_collected = load(collected_file)
    old_uncollected = load(uncollected_file)
    old_collected.update(collected)
    old_uncollected.update(uncollected)
    with open(collected_file, 'w+') as f:
        json.dump(old_collected, f)
    with open(uncollected_file, 'w+') as f:
        json.dump(old_uncollected, f)


def query_per_ip(api, ip):
    logging.info("Downloading ip: %s" % ip)
    try:
        url = "https://api.shodan.io/shodan/host/%s?key=%s" % (ip, SHODAN_API_KEY)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        f = urllib.request.urlopen(urllib.request.Request(url=url, headers=headers))
        data = f.read()
        encoding = f.info().get_content_charset('utf-8')
        JSON_object = json.loads(data.decode(encoding))

        file_name = "/media/z1xuan/Elements/shodan/nodes/%s/banner" % ip.replace('.', '_')
        with open(file_name, 'w+') as f:
            json.dump(JSON_object, f)
        with open(file_name, 'rb') as f_in:
            with gzip.open('%s.gz' % file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file_name)
        return True
    except urllib.error.HTTPError as e:
        logging.warning("No information available for that IP.")
        return False


def load(file_name="data/id_host_data"):
    with open(file_name) as f:
        data = json.load(f)
    return data


def main():
    file_name = "data/id_host_data"
    copy_cmd = "cp %s /media/z1xuan/Elements/shodan/id_host_data" % file_name
    move_data_local(file_name, copy_cmd)
    mkdir()
    collect("/media/z1xuan/Elements/shodan/collected", "/media/z1xuan/Elements/shodan/uncollected")


def mkdir():
    data = load()
    for entry in data:
        for ip in data[entry]:
            directory = "/media/z1xuan/Elements/shodan/nodes/%s" % ip.replace('.', '_')
            try:
                os.mkdir(directory)
                logging.info("Created %s" % directory)
            except OSError as error:
                logging.warning(error)


if __name__ == "__main__":
    log_name = "log/query_shodan.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    cmd_logger()
    main()
