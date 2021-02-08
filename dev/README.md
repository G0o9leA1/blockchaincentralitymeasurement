# Requirement:
* Python Version:
    ```
    python_version >= 3.73
    ```
* Numpy, pycurl, openpyxl, pydriller, dateutil:
    ```
    pip install numpy
    pip install pycurl
    pip install openpyxl
    pip install pydriller
    pip install dateutil
    ```



# Usage:
* repo_crawler.py: Collect repositories metadata from GitHub
* cloner.py: Download Git repo base on metadata
* dev_statics.py: Process commit data and build as commit table locally
* commit_crawler.py: Download commit data from GitHub API
* id.py: Mapping commit table to contributor
* contribution.py: Calculate developer contribution distribution
* language.py: Calculate language centrality
* export.py: Utilities to export json file into excel file
* manual.py, description.py: Utilities script for paperwork     


# Notes:
If this code is published public, please remove all GitHub token!