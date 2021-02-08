import json
import subprocess
from .top import get_top
from .utils import pprint

btc_file_list = get_top("bitcoin")
eth_file_list = get_top("ethereum")


def get_loc(file_path):
    result = subprocess.run(["lib/cloc", file_path, "--json"], check=True, stdout=subprocess.PIPE, timeout=1800).stdout
    return json.loads(result)["SUM"]["nFiles"]


loc_dict = dict()
for file in btc_file_list:
    file_path = "/home/z1xuan/Desktop/repo/bitcoin/%s" % file.replace("/", "_")
    try:
        loc_dict[file] = get_loc(file_path)
        print("done")
    except BaseException:
        pass


for file in eth_file_list:
    file_path = "/home/z1xuan/Desktop/repo/ethereum/%s" % file.replace("/", "_")
    try:
        loc_dict[file] = get_loc(file_path)
        print("done")
    except BaseException:
        pass


with open("../data/file.json", "w+") as f:
    json.dump(loc_dict, f)
#
# for file in btc_file_list:
#     if loc_dict[file] == 0:
#         print(file)
#
# for file in eth_file_list:
#     if loc_dict[file] == 0:
#         print(file)

