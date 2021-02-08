import os
import time
from datetime import timedelta
from datetime import datetime
from .ethnode_data import cmd_logger
import logging
file_name = "log/ethnode_data.log"
move_cmd = "mv tmp/*.json history"
copy_local_cmd = "cp tmp/*.json history"


def move_data_local(file_name, move_cmd):
    modified_time = datetime.fromtimestamp(os.stat(file_name).st_mtime)
    current_time = datetime.fromtimestamp(time.time())
    if timedelta(hours=23) > current_time-modified_time > timedelta(minutes=30):
        logging.info(move_cmd)
        os.system(move_cmd)
        return True
    return False


def compress_data():
    timestamp = int(time.time() * 1000)
    file_name = "%i.tar.gz" % timestamp
    compress_cmd = "tar -czf %s history/*.json" % file_name
    logging.info(compress_cmd)
    os.system(compress_cmd)
    copy_cmd = "cp %s /media/z1xuan/Elements/eth_node" % file_name
    logging.info(copy_cmd)
    os.system(copy_cmd)
    move_cmd = "mv %s history" % file_name
    logging.info(move_cmd)
    os.system(move_cmd)
    clear_cmd = "rm history/*.json"
    os.system(clear_cmd)
    logging.info(clear_cmd)


def back_up(sleep_time=86400):
    while 1:
        try:
            flag = move_data_local(file_name, move_cmd)
            while not flag:
                flag = move_data_local(file_name, move_cmd)
                time.sleep(30)
            compress_data()
        except BaseException:
            pass
        time.sleep(sleep_time)


if __name__ == "__main__":
    log_name = "log/back_up.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    cmd_logger()
    back_up()
