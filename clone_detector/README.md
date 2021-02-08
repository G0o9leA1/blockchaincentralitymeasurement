# Requirement:
* Python Version:
    ```
    python_version >= 3.73
    ```
* Nodejs, jscpd
    ```
    sudo apt install nodejs
    npm install -g jscpd
    ```

# Usage:
* dupl_detect.py: integration function with dupl code clone detection engine
* deckard_detect.py: integration function with deckard code clone detection engine
* jscpd_detect.py: integration function with jscpd code clone detection engine
* language_type.py: providing necessary language information
* preprocess.py: preprocess for clone detection
* launcher.py: multiprocess launcher for main.py
* main.py: code clone function main entrance 
* similar.py: calculate similarity score using Jaccard coefficient 
* cloc.py: calculate lines of code     
* utils.py: general utilities functions 
* log_parser.py: utilities functions for parsing log history  
* top.py: function for detect code clone in a subset
