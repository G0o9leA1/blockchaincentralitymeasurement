import json
with open("repos/ethereum.json") as f:
    data = json.load(f)
with open('c_a_data.json') as f:
    c_a = json.load(f)
tmp = list()
for entry in data:
    try:
        if data[entry]["watchers_count"] < 5 and data[entry]["forks_count"] < 5 and c_a[entry.replace('/', '_')][0] >= 5:
            tmp.append(entry)
    except BaseException:
        pass
print(len(tmp))
