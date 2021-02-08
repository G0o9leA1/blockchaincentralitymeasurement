import json
import getpass
import shutil
import os
import time


while(1):
    with open("log/done.json") as f:
        done = json.load(f)

    with open("log/repos.log") as f:
        username = getpass.getuser()
        for line in f.readlines():
            data = line.split()
            if len(data) == 7:
                [date_data, time_data, level, src1, src2, engine, report_loc] = data
                level = level[:-1]
                prefix = "/home/%s/Desktop/clone_detector/tmp/ramdisk" % username
                appendx = report_loc[report_loc.find(prefix)+len(prefix):]
                new_loc = "/home/%s/Desktop/clone_detector/out%s" % (username, appendx)
                if report_loc is None:
                    continue
                if src1 not in done:
                    done[src1] = dict()

                elif src2 not in done[src1]:
                    try:
                        os.mkdir(os.path.dirname(new_loc))
                        shutil.move(report_loc, new_loc)
                        done[src1][src2] = new_loc
                        print(new_loc)
                    except BaseException:
                        pass
                else:
                    continue

            else:
                continue
                [date_data, time_data, level, src1, src2, engine] = data[:6]
                exception = ' '.join(data[6:])
                print(exception)

    with open("log/done.json", "w+") as f:
        json.dump(done, f)
    time.sleep(1800)
