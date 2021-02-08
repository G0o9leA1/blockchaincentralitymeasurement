import json
import os
import gzip

def stats():
    with open("data/id_host_data") as f:
        data = json.load(f)
    host_id = dict()
    collected = dict()
    uncollected = dict()
    dup = 0
    for entry in data:
        for host in data[entry]:
            if host not in host_id:
                host_id[host] = [entry]
            else:
                dup += 1
                host_id[host].append(entry)
    print(dup)
    ip_counter = 0
    un_ip = 0
    for file_name in os.listdir("/media/z1xuan/Elements/shodan/nodes"):
        ip = file_name.replace("_", ".")
        if "banner.gz" in os.listdir("/media/z1xuan/Elements/shodan/nodes/"+file_name):
            ip_counter += 1
            for id in host_id[ip]:
                if id not in collected:
                    collected[id] = [ip]
                else:
                    collected[id].append(ip)
        else:
            un_ip += 1
            for id in host_id[ip]:
                if id not in uncollected:
                    uncollected[id] = [ip]
                else:
                    uncollected[id].append(ip)
    with open("shodan/collected", "w+") as f:
        json.dump(collected, f)
    with open("shodan/uncollected", "w+") as f:
        json.dump(uncollected, f)

    print(ip_counter, len(collected), un_ip, len(uncollected))


def uncompress(file_list):
    vuln = 0
    ports = 0
    for file_name in file_list:
        compressed = gzip.GzipFile(file_name, 'rb')
        data = compressed.read()
        compressed.close()
        data = json.loads(data.decode("utf-8"))
        if "vulns" in data:
            vuln += 1
        if len(data["ports"]) != 0:
            ports += 1

    print(vuln, ports)


def get_file_list():
    file_list = list()
    for file_name in os.listdir("/media/z1xuan/Elements/shodan/nodes"):
        ip = file_name.replace("_", ".")
        if "banner.gz" in os.listdir("/media/z1xuan/Elements/shodan/nodes/"+file_name):
            file_list.append("/media/z1xuan/Elements/shodan/nodes/" + file_name + "/banner.gz")
    return file_list

