import json
import time
import subprocess
import sys
import logging
from .repo_crawler import cmd_logger


def load_repo(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def load_tracking(tracking):
    tracked = list()
    with open(tracking) as f:
        for line in f.readlines():
            repo_name = line.split()[0]
            tracked.append(repo_name)
    return tracked


def generate_repo_tracking(repos, file_path):
    with open(file_path, 'w+') as f:
        for entry in repos:
            write_data = "%s %s\n" %(entry, repos[entry]["clone_url"])
            logging.info(write_data)
            f.write(write_data)


def track(repo_name, file_path):
    timestamp = str(int(time.time()))
    with open(file_path, 'a+') as f:
        write_data = "%s %s\n" % (timestamp, repo_name)
        f.write(write_data)


def clone_per_repo(repo_name, url, cwd, tracker):
    file_name = repo_name.replace("/", "_")
    cmd = ['git', 'clone', "--progress", "--verbose",  url, file_name]
    output = str()
    errout = str()
    logging.info("Append %s" % repo_name)
    try:
        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=cwd)
    except subprocess.CalledProcessError as process:
        output = process.stdout
        errout = process.stderr
        pass
    if output != "":
        logging.info(output)
    if errout != "":
        logging.info(errout)
    track(repo_name, tracker)


def clone_all(tracking, tracker, cwd):
    logging.info("New Clone Job")
    with open(tracking) as f:
        for line in f.readlines():
            repo_name, url = line.split()
            url = url.strip('\n')
            clone_per_repo(repo_name, url, cwd, tracker)


def increment_clone(tracking, tracker, cwd):
    logging.info("Increment Clone Job")
    with open(tracking) as f1:
        with open(tracker) as f2:
            downloaded = list()
            for line in f2.readlines():
                downloaded.append(line.split()[1].strip('\n'))

        for line in f1.readlines():
            repo_name, url = line.split()
            url = url.strip('\n')
            if repo_name not in downloaded:
                clone_per_repo(repo_name, url, cwd, tracker)
                track(repo_name, tracker)


def update_tracking(file_path, tracking):
    logging.info("Update tracking")
    repos = load_repo(file_path)
    tracked = load_tracking(tracking)
    with open(tracking, "a+") as f:
        for repo in repos:
            if repo not in tracked:
                write_data = "%s %s\n" % (repo, repos[repo]["clone_url"])
                logging.info(write_data.strip('\n'))
                f.write(write_data)


def download(topic, tracker, tracking, cwd):
    update_tracking("/home/z1xuan/Desktop/eth_dev/repos/%s.bin" % topic, tracking)
    clone_all(tracking, tracker, cwd)
    # increment_clone(tracking, tracker, cwd)


# git fetch -p origin

def main(topic):
    log_name = "log/clone.log"
    logging.basicConfig(filename=log_name, filemode='a+',
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%y-%b-%d %H:%M:%S',
                        level=logging.INFO)
    cmd_logger()
    tracker = "/home/z1xuan/Desktop/repo/%s/tracker" % topic
    tracking = "/home/z1xuan/Desktop/repo/%s/tracking" % topic
    cwd = "/home/z1xuan/Desktop/repo/%s/" % topic
    download(topic, tracker, tracking, cwd)


if __name__ == '__main__':
    main(sys.argv[1])
