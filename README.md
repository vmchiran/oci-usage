# oci-usage-reports

# Pre-requisites
- Python3
- oci cli

# How to run
- Extracting reports for the current date
    `./run_daily_getUsageReportsOCI.sh`
- Running the python script with options
    `python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/dir --targetDate 2020-01-20`