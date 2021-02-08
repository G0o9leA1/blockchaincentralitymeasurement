import shutil
import os
import json
import random
import string


def pprint(obj):
    print(json.dumps(obj, indent=2))


def get_dir_name(first, second):
    return "%s_%s" % (first, second)


def listdir(src, ignore_dir={".git"}, ignore_file={".gitignore", ".gitattributes"}):
    file_list = list()
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ignore_dir]
        files[:] = [f for f in files if f not in ignore_file]
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def copy_dir(src, dst):
    map_table = dict()
    try:
        shutil.copytree(src, dst, ignore_dangling_symlinks=True, symlinks=True)
    except IOError:
        exit()
    for file_name in listdir(src):
        map_table["%s%s" %(dst, file_name[len(src):])] = file_name
    return map_table


def remove_dir(src):
    shutil.rmtree(src)


def random_str(n=30):
    s = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    return s


if __name__ == "__main__":
    pprint(copy_dir("/home/z1xuan/Desktop/repo/ethereum/0age_AttributeRegistry", "/home/z1xuan/Desktop/clone_detector/here"))
    with open("report/jscpd-report.json") as f:
        data = json.load(f)
    pprint(data["statistics"])
    print(len(listdir("here")))