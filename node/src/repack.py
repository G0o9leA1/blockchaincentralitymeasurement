import os
import time
archive = os.listdir("history/")

for file_name in archive:
    name, suffix = os.path.splitext(file_name)
    if suffix == ".tar":
        decompress_cmd = "tar -xf history/%s" % file_name
        repack_cmd = "tar -czf history/%s.tar.gz history/*.json" % name
        remove_cmd = "rm -rf history/*.json"
        os.system(decompress_cmd)
        os.system(repack_cmd)
        os.system(remove_cmd)
        print(repack_cmd)