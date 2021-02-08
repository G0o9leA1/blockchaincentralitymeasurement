import io
import json
import os
import logging
import subprocess
from copy import deepcopy
from shutil import copyfile
from .utils import random_str, copy_dir, remove_dir


def get_output_dir():
    return os.path.abspath("tmp/ramdisk/%s" % random_str())


def config(file_pattern, src_dir):
    copy_dst = "%s/config" % src_dir
    copyfile("config", copy_dst)
    with open(copy_dst) as f:
        data = f.readlines()
    exe_path = os.path.abspath("lib/Deckard")
    data[30] = "FILE_PATTERN='%s'\n" % file_pattern
    data[32] = "SRC_DIR='%s'\n" % src_dir
    data[44] = "DECKARD_DIR='%s'\n" % exe_path
    data[55] = "VECTOR_DIR='%s/vectors'\n" % src_dir
    data[57] = "CLUSTER_DIR='%s/clusters'\n" % src_dir
    data[59] = "TIME_DIR='%s/times'\n" % src_dir
    with open(copy_dst, 'w') as f:
        f.writelines(data)


def post_process(map1, map2, output_file_name, dir_name):
    with open(output_file_name, 'rt') as f:
        data = f.read()
    for k, v in map1.items():
        data = data.replace(k, v)
    for k, v in map2.items():
        data = data.replace(k, v)
    remove_dir(dir_name)
    os.makedirs(dir_name)
    output_file_name = "%s/deckard-report.json" % dir_name
    buf = io.StringIO(data)
    report = list()
    sub = list()
    for line in buf.readlines():
        if line != '\n':
            sub.append(line.strip('\n').split())
        else:
            report.append(deepcopy(sub))
            sub.clear()
    with open(output_file_name, "w+") as f:
        json.dump(report, f)
    return output_file_name


def deckard(src1, src2, lan):
    config_list = ['*.java', '*.c', '*.php', '*.sol', '*.go']
    dir_name = get_output_dir()
    dst1 = "%s/src1" % dir_name
    dst2 = "%s/src2" % dir_name
    dst2src1_map = (copy_dir(src1, dst1))
    dst2src2_map = (copy_dir(src2, dst2))
    config(config_list[lan], dir_name)
    exe_path = os.path.abspath("lib/Deckard/scripts/clonedetect/deckard.sh")
    try:
        subprocess.run([exe_path],
                   cwd=dir_name, check=True, shell=True, stdout=subprocess.PIPE, timeout=1800)
        output_file_name = "%s/clusters/post_cluster_vdb_30_0_allg_0.70_30" % dir_name
        output_file_name = post_process(dst2src1_map, dst2src2_map, output_file_name, dir_name)
        return output_file_name
    except BaseException:
        remove_dir(dir_name)
        return None

def main(src1, src2, lan):
    log_name = "log/language.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    try:
        output_file_loc = deckard(src1, src2, lan)
        logging.info("%s %s deckard %s" % (src1, src2, output_file_loc))
    except BaseException as e:
        logging.critical("%s %s deckard %s" % (src1, src2, e))
