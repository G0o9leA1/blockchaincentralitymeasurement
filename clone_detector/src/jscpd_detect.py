import os
import logging
import subprocess
from .utils import remove_dir, random_str, copy_dir


def get_output_dir():
    return os.path.abspath("tmp/ramdisk/%s" % random_str())


def change_file_md(src):
    if os.path.islink(src):
        return src
    file_name, ext = os.path.splitext(src)
    if ext[1:].lower() not in {"png", "csv", "jpg", "pyc", "pdf", "dll", "gif", "bmp"}:
        ext = ".md"
        new_name = file_name + ext
        while os.path.isfile(new_name) or os.path.isdir(new_name):
            new_name = "%s%s" %(file_name, random_str(5)) + ext
        os.rename(src, new_name)
        return new_name
    return src


def pre_process(topic, project_name, language_data, dir_name, username):
    md_map = dict()
    pro_dir_name = "/home/%s/Desktop/repo/%s/%s" % (username, topic, project_name.replace('/', '_'))
    for src in language_data[topic][project_name]["unidentified"]:
        if os.path.islink(src):
            continue
        tmp_src = "%s%s" %(dir_name, src[len(pro_dir_name):])
        new_src = change_file_md(tmp_src)
        if tmp_src != new_src:
            md_map[new_src] = tmp_src

    return md_map


def post_process(map1, map2, json_file, dir_name):
    with open(json_file, "rt") as f:
        data = f.read()
    for k, v in map2.items():
        data = data.replace(k, v)
    for k, v in map1.items():
        data = data.replace(k, v)
    remove_dir(dir_name)
    os.makedirs(dir_name)
    with open(json_file, "wt+") as f:
        f.write(data)


def jscpd(topic1, project_name1, src1, topic2, project_name2, src2, language_data, username):
    dir_name = get_output_dir()
    dst1 = "%s/src1" % dir_name
    dst2 = "%s/src2" % dir_name
    dst2src_map = copy_dir(src2, dst2)
    dst2src_map.update(copy_dir(src1, dst1))
    md_map = pre_process(topic2, project_name2, language_data, "%s/src2" % dir_name, username)
    md_map.update(pre_process(topic1, project_name1, language_data, "%s/src1" % dir_name, username))
    for entry in md_map:
        os.rename(entry, md_map[entry])
    try:
        subprocess.run(["jscpd", '.', "-k", "30", "-r", "json", "-o", '.', "-a", "true"],
                   check=True, cwd=dir_name, stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=1800)
        output_file_name = "%s/jscpd-report.json" % dir_name
        post_process(dst2src_map, md_map, output_file_name, dir_name)
        return output_file_name
    except BaseException:
        remove_dir(dir_name)
        return None


def main(topic1, project_name1, src1, topic2, project_name2, src2, language_data):
    log_name = "log/repos.log"
    logging.basicConfig(filename=log_name, filemode='a+', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%y-%b-%d %H:%M:%S', level=logging.INFO)
    try:
        output_file_loc = jscpd(topic1, project_name1, src1, topic2, project_name2, src2, language_data, username)
        logging.info("%s %s jscpd %s" % (src1, src2, output_file_loc))
    except BaseException as e:
        logging.critical("%s %s jscpd %s" % (src1, src2, e))


if __name__ == "__main__":
    import json
    with open("language.json") as f:
        language_data = json.load(f)
    jscpd("bitcoin", "momenbasel/bitstable", "/home/z1xuan/Desktop/repo/bitcoin/momenbasel_bitstable", "bitcoin",
         "FabricLabs/chat.fabric.pub", "/home/z1xuan/Desktop/repo/bitcoin/FabricLabs_chat.fabric.pub", language_data, username)
