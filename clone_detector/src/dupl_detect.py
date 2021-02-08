import io
import os
import json
import subprocess
import logging
from .utils import random_str, copy_dir, remove_dir


def get_output_dir():
    return os.path.abspath("tmp/ramdisk/%s" % random_str())


def post_process(map1, map2, res, dir_name):
    res = res.decode('utf-8')
    for k, v in map1.items():
        res = res.replace(k, v)
    for k, v in map2.items():
        res = res.replace(k, v)
    buf = io.StringIO(res)
    report = list()
    for line in buf.readlines():
        first_file = line.split(':')[0]
        first_lines = (line.split(':')[1]).split("-")
        second_file, second_lines = (line[line.find("duplicate of")+13:]).split(":")
        second_lines = second_lines.split('\n')[0].split("-")
        report.append({"first_file": first_file,
                       "first_lines": first_lines,
                       "second_file": second_file,
                       "second_lines": second_lines})
    remove_dir(dir_name)
    os.makedirs(dir_name)
    with open("%s/dupl-report.json" % dir_name, 'w+') as f:
        json.dump(report, f)


def dupl(src1, src2):
    dir_name = get_output_dir()
    dst1 = "%s/src1" % dir_name
    dst2 = "%s/src2" % dir_name
    dst2src1_map = (copy_dir(src1, dst1))
    dst2src2_map = (copy_dir(src2, dst2))
    exe_path = os.path.abspath("lib/dupl")
    try:
        result = subprocess.run([exe_path, "-plumbing", '.'],
                            cwd=dir_name, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
        post_process(dst2src1_map, dst2src2_map, result.stdout, dir_name)
        output_file_name = "%s/dupl-report.json" % dir_name
        return output_file_name
    except BaseException:
        remove_dir(dir_name)
        return None

def main(src1, src2):
    src1 = os.path.abspath(src1)
    src2 = os.path.abspath(src2)
    log_name = "log/repos.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    try:
        output_file_loc = dupl(src1, src2)
        logging.info("%s %s dupl %s" % (src1, src2, output_file_loc))
    except BaseException as e:
        logging.critical("%s %s dupl %s" % (src1, src2, e))


if __name__ == "__main__":
    main()
