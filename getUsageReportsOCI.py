import oci
import os
import sys
import argparse
from datetime import datetime
from datetime import date

"""
Script used to download Usage Reports from an OCI tenant using date filters.

Authors
- valeria.chiran@oracle.com
- ionut.vladu@oracle.com

Script based on this article: https://docs.cloud.oracle.com/iaas/Content/Billing/Tasks/accessingusagereports.htm
OCI CLI Python SDK Documentation: https://oracle-cloud-infrastructure-python-sdk.readthedocs.io

How to run
Examples:
python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --targetDate 2020-01-20
python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --afterDate 2020-01-20
python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --beforeDate 2020-01-20
python3 getUsageReportsOCI.py --ociProfile DEFAULT --destDir /home/opc/oci-usage --betweenDates 2019-12-20/2020-01-20
"""

### Global variables ###

# usage reports namespace - leave as it is!!
usage_report_namespace = "bling"

# Download all usage and cost files. You can comment out based on the specific need:
# prefix_file = ""                     #  For cost and usage files
prefix_file = "reports/cost-csv"   #  For cost
# prefix_file = "reports/usage-csv"  #  For usage

def get_object_list(config_file_profile):
    """
    Method used to get the list of all objects from the usage reports bucket
    """
    # read the config file and create the object storage client
    config = oci.config.from_file(oci.config.DEFAULT_LOCATION, config_file_profile)
    object_storage = oci.object_storage.ObjectStorageClient(config)
    
    usage_report_bucket = config["tenancy"]

    # added fields name, timeCreated and size to the report_bucket_objects Object so we can filter using them
    report_bucket_objects = object_storage.list_objects(usage_report_namespace, usage_report_bucket, fields="name,timeCreated,size", prefix=prefix_file)

    return {"object_storage": object_storage, "report_bucket_objects": report_bucket_objects, "usage_report_bucket": usage_report_bucket}


def filter_reports(objects, destintation_path, **kwargs):
    """
    Method used to loop over all the usage report files available on the tenant
    
    Based on the argument passed (targetDate, beforeDate, afterDate or betweenDates) it will filter the reports to download
    """
    # Create the destination path if it doesn't exist
    if not os.path.exists(destintation_path):
        os.mkdir(destintation_path)
    
    # print(objects["report_bucket_objects"].data.objects)
    
    # loop over all objects in bucket
    for o in objects["report_bucket_objects"].data.objects:
        # print(f"Found file {o.name} created on {o.time_created.date()}")
                
        # use the date filters to download only the desired reports
        for key, value in kwargs.items():
            # print(f"Key is {key} and value is {value}")
            # download only the report from the targetDate
            if key == "targetDate":
                if o.time_created.date() == datetime.strptime(value, "%Y-%m-%d").date():
                    download_report(o, destintation_path, objects)
            # download only the reports that are before the beforeDate
            elif key == "beforeDate":
                if o.time_created.date() < datetime.strptime(value, "%Y-%m-%d").date():
                    download_report(o, destintation_path, objects)
            # download only the reports that are after the afterDate
            elif key == "afterDate":
                if o.time_created.date() > datetime.strptime(value, "%Y-%m-%d").date():
                    download_report(o, destintation_path, objects)
            # download only the reports that are between the two dates from betweenDates
            elif key == "betweenDates":
                if (o.time_created.date() >= datetime.strptime(value.split("/")[0], "%Y-%m-%d").date() and 
                    o.time_created.date() <= datetime.strptime(value.split("/")[1], "%Y-%m-%d").date()):
                    download_report(o, destintation_path, objects)
            

def download_report(obj, destintation_path, objects):
    """
    Method used to download and write to disk report file
    """
    # get details for the object
    object_details = objects["object_storage"].get_object(usage_report_namespace, objects["usage_report_bucket"], obj.name)
    
    # get the last 2 parts of the filename
    filename = str(obj.time_created.date()) + "-" + obj.name.rsplit("/", 2)[-2] + "-" + obj.name.rsplit("/", 2)[-1]
    
    print(f"Downloading the report from {obj.time_created.date()} named {obj.name} ...")
    
    # download and write to disk the report
    with open(destintation_path + "/" + filename, "wb") as f:
        for chunk in object_details.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)
            
    print(f"Finished downloading report '{obj.name}' here: '{destintation_path}/{filename}'\n")


def main():
    """
    Main method
    """  
    # Arguments to be pased when executing the script
    parser = argparse.ArgumentParser(description="Download Usage Reports. Please use only one of the Date arguments at a time.")
    parser.add_argument("--ociProfile", help=f"OCI Profile. Ex: python {sys.argv[0]} --ociProfile tenantName")
    parser.add_argument("--destDir", help=f"Download directory. Ex: python {sys.argv[0]} --destDir ~/oci-usage")
    parser.add_argument("--targetDate", help=f"Download a report from a specific date. Ex: python {sys.argv[0]} --targetDate 2020-01-20")
    parser.add_argument("--beforeDate", help=f"Download all reports available before a specific date. Use the date of tomorrow for all reports. Ex: python {sys.argv[0]} --beforeDate 2020-01-20")
    parser.add_argument("--afterDate", help=f"Download all reports available after a specific date. Ex: python {sys.argv[0]} --afterDate 2020-01-20")
    parser.add_argument("--betweenDates", help=f"Download all reports available between two dates (inclusive). Ex: python {sys.argv[0]} --betweenDates 2019-12-20/2020-01-20")
    args = parser.parse_args()
        
    # if there are no arguments passed
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    # if there are more than three arguments passed
    elif len(sys.argv) > 8:
        print()
        print("ERROR - Too many arguments passed.")
        print()
        print("Please use the -h argument to find out how to use the script")
        print()
        print(f"Example: python {sys.argv[0]} -h")
        sys.exit()
        
    # Get the object list for the configured tenant
    config_file_profile = args.ociProfile
    print(f"config_file_profile: {config_file_profile} ...\n")
    objects = get_object_list(config_file_profile)

    destintation_path = args.destDir
    print(f"Downloading reports on: {args.destDir} ... \n")
        
    # pass on the argument to the filter_reports method
    if args.targetDate:
        print(f"Searching for reports on: {args.targetDate} ... \n")
        filter_reports(objects, destintation_path, targetDate=args.targetDate)
    elif args.beforeDate:
        print(f"Searching for reports before: {args.beforeDate} ... \n")
        filter_reports(objects, destintation_path, beforeDate=args.beforeDate)
    elif args.afterDate:
        print(f"Searching for reports after: {args.afterDate} ... \n")
        filter_reports(objects, destintation_path, afterDate=args.afterDate)
    elif args.betweenDates:
        print(f"Searching for reports between: {args.betweenDates.split('/')[0]} and {args.betweenDates.split('/')[1]} ... \n")
        filter_reports(objects, destintation_path, betweenDates=args.betweenDates)
           
    
    
if __name__ == "__main__":
    main()
    