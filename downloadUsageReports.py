import oci
import os
import sys

# python3 downloadUsageReports.py my_oci_profile
#
# Ref. https://docs.cloud.oracle.com/iaas/Content/Billing/Tasks/accessingusagereports.htm
#
# This script downloads all of the usage reports for a tenancy (specified in the config file)
#
# Pre-requisites: Create an IAM policy to endorse users in your tenancy to read usage reports from the OCI tenancy
#
# Example policy:
# define tenancy usage-report as ocid1.tenancy.oc1..aaaaaaaaned4fkpkisbwjlr56u7cj63lf3wffbilvqknstgtvzub7vhqkggq
# endorse group group_name to read objects in tenancy usage-report
#

if not len(sys.argv) == 2:
  print("Missing argument oci_profile. Script will exit.")
  exit(1)

oci_profile = sys.argv[1]
print("Collecting usage reports for oci_profile " + oci_profile)

usage_report_namespace = 'bling'

# Download all usage and cost files. You can comment out based on the specific need:
prefix_file = ""                     #  For cost and usage files
# prefix_file = "reports/cost-csv"   #  For cost
# prefix_file = "reports/usage-csv"  #  For usage

# Update these values
destintation_path = '/home/opc/oci-usage/' + oci_profile

# Make a directory to receive reports
if not os.path.exists(destintation_path):
  os.mkdir(destintation_path)

# Get the list of usage reports
config = oci.config.from_file(oci.config.DEFAULT_LOCATION, oci_profile)
usage_report_bucket = config['tenancy']
object_storage = oci.object_storage.ObjectStorageClient(config)
report_bucket_objects = object_storage.list_objects(usage_report_namespace, usage_report_bucket, prefix=prefix_file)

for o in report_bucket_objects.data.objects:
  print('Found file ' + o.name)
  filename = o.name.rsplit('/', 1)[-1]
  object_details = object_storage.get_object(usage_report_namespace,usage_report_bucket,o.name)

  with open(destintation_path + '/' + filename, 'wb') as f:
    for chunk in object_details.data.raw.stream(1024 * 1024, decode_content=False):
      f.write(chunk)

  print('----> File ' + o.name + ' Downloaded\n')