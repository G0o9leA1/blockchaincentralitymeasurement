import json
import time
import logging
from .ethnode_data import cmd_logger


def show(old_node_number=0, old_ip_number=0):
    with open("data/ethnode_org_data") as f:
        data = json.load(f)

    update_time = int(data["update_time"]) / 1000

    with open("data/id_host_data") as f:
        data = json.load(f)

    node_number = len(data)
    ip_number = 0
    for entry in data:
        ip_number += len(data[entry])

    flag = False
    if node_number != old_node_number or ip_number != old_ip_number:
        flag = True
        logging.info("Last Update: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(update_time)))
        logging.info("Node Number: " + str(node_number))
        logging.info("IP Number:   " + str(ip_number))

    return [node_number, ip_number, flag]


if __name__ == "__main__":
    log_name = "log/statics.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    cmd_logger()
    [node_number, ip_number, flag] = show()
    while True:
        if flag:
            time.sleep(300)
        try:
            [node_number, ip_number, flag] = show(node_number, ip_number)
        except Exception:
            pass
