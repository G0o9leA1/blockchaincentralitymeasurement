# importing csv module 
import csv 
import json
import re
from collections import OrderedDict
from .shodan_statics import get_file_list
import gzip
# csv file name
from copy import deepcopy


def dump():
    filename = "allitems.csv"
    # name, status, description, reference, phase, votes, comments
    cves = list()
    with open(filename, encoding="utf8", errors='ignore') as f:
        f_csv = csv.reader(f)
        counter = 0
        headers = list()
        for row in f_csv:
            if counter <= 9:
                headers.append(row)
            else:
                cve_detail = OrderedDict()
                cve_detail["name"], cve_detail["status"], cve_detail["description"], cve_detail["reference"], cve_detail["phase"], cve_detail["votes"], cve_detail["comments"] = row
                cves.append(cve_detail)
            counter += 1
    with open("allitems.json", 'w+') as f:
        json.dump(cves, f)


def load():
    with open("allitems.json") as f:
        data = json.load(f)
    return data


type_dict = dict()
cve_db = load()
# hostname, cve, type


def search_type(cve_id):
    if cve_id in type_dict:
        return type_dict[cve_id]
    res = list()
    for entry in cve_db:
        if entry["name"] == cve_id:
            for keyword in keywords:
                if re.search(keyword, entry["description"], re.IGNORECASE):
                    res.append(keyword)
            break
    type_dict[cve_id] = res
    return res


keywords = ["buffer overflow", "code execution", "denial of service", "arbitrary commands", "bypass authentication", "privilege escalation", "gain root access", "gain access", "REJECT", "RESERVED", "memory corruption", "directory traversal", "username enumeration", "access freed memory", "man-in-the-middle", "execute arbitrary code", "XSS", "arbitrary files", "execute arbitrary OS commands", "hijack web sessions", "heartbleed"]
# file_list = get_file_list()
# for file_name in file_list:
#     compressed = gzip.GzipFile(file_name, 'rb')
#     data = compressed.read()
#     compressed.close()
#     data = json.loads(data.decode("utf-8"))
#     if "vulns" in data:
#         host_cve[data["ip_str"]] = list()
#         for cve in data["vulns"]:
#             cve_type = search_type(cve)
#             host_cve[data["ip_str"]].append({cve:cve_type})
#
# with open("cve_type.json", "w+") as f:
#     json.dump(type_dict, f)
#
# num = 0
# for key in host_cve:
#     detail_num = 0
#     for entry in host_cve[key]:
#         detail_num += len(entry.values())
#     if detail_num == 0:
#         num += 1
#     else:
#         print(detail_num)
# print(num)


def categorize(keywords, uncate, host_cve):
    ret = set()
    copy_uncate = deepcopy(uncate)
    for ip in uncate:
        for cve in host_cve[ip]:
            for key in cve:
                for keyword in keywords:
                    if keyword in cve[key]:
                        ret.add(ip)
                        if ip in copy_uncate:
                            copy_uncate.remove(ip)
    uncate = deepcopy(copy_uncate)
    return [ret, uncate]

with open("host_cve.json") as f:
    host_cve = json.load(f)
uncate = set()
for entry in host_cve:
    uncate.add(entry)
print(len(uncate))
[ret, uncate] = categorize(["code execution", "arbitrary commands", "execute arbitrary code", "execute arbitrary OS commands"], uncate, host_cve)
print(len(ret))
[ret, uncate] = categorize(["denial of service"], uncate, host_cve)
print(len(ret))
[ret, uncate] = categorize(["directory traversal", "arbitrary files"], uncate, host_cve)
print(len(ret))
[ret, uncate] = categorize(["username enumeration", "arbitrary files"], uncate, host_cve)
print(len(ret))
print(uncate)
ip_list = set()
dos_list = set()
by_pass = set()
for entry in host_cve:
    for cve in host_cve[entry]:
        for key in cve:
            if "code execution" in cve[key] or "arbitrary commands" in cve[key] or "execute arbitrary code" in cve[key] or "execute arbitrary OS commands" in cve[key]:
                ip_list.add(entry)
for entry in host_cve:
    for cve in host_cve[entry]:
        for key in cve:
            if "denial of service" in cve[key]:
                if entry not in ip_list:
                    dos_list.add(entry)
for entry in host_cve:
    for cve in host_cve[entry]:
        for key in cve:
            if "bypass authentication" in cve[key]:
                if entry not in ip_list and entry not in dos_list:
                    by_pass.add(entry)
print(len(ip_list))
print(len(dos_list))
print(len(by_pass))