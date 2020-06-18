# oci-usage-reports

# Prerequisites
- Python3
- oci cli

# How to run
- Extracting reports for the current date

    `./run_daily_getUsageReportsOCI.sh`

- Running the python script with date options

    `python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --targetDate 2020-01-20`

    `python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --afterDate 2020-01-20`

    `python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --beforeDate 2020-01-20`
    
    `python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --betweenDates 2019-12-20/2020-01-20`

- Running the python script to download all the reports

    `python3 downloadUsageReports.py my_oci_profile`