# PDupdateServices

Update Services contained within a list to enable creating Alerts and Notifications

## Installation

First, have python 3 installed. Then:

    python3 -m venv venv              # create a virtual environment
    . venv/bin/activate               # activate it
    pip install -r requirements.txt   # install dependencies. use pip3 if no pip

## Usage

    ./updateService.py -a API_Token -f CSV_File -c Change_to_Make > output.txt

    optional arguments:
    -h, --help            show this help message and exit
    -a API, --api API     pagerduty api token
    -f FILE, --file FILE  csv filename with Services Name and Services
                        Obfuscated ID fields
    -c CHANGE, --change CHANGE
                        change to service 'feature:setting', eg
                        'alert_creation:create_incidents' or
                        'acknowledgement_timeout:10'

    API_Token can be hardcoded to line 23 of updateService.py
    Service IDs can be hardcoded to line 26 of updateService.py instead of CSV_File
    Change_to_Make is hardcoded to 'alert_creation:create_alerts_and_incidents'
      but can be overridden with -c argument to something like 'acknowledgement_timeout:1'

    You can find or add a new API Token by following these instructions https://support.pagerduty.com/docs/generating-api-keys
