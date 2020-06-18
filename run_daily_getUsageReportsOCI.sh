#!/bin/bash
#############################################################################################################################
# Author - Valeria Chiran, January 2020 - Updated June 2020
#
# Extract usage report for the current date
#
# Example crontab set:
# 50 5,11,17,23 * * * /home/opc/oci-usage/run_daily_getUsageReportsOCI.sh
#############################################################################################################################
DATE=`date '+%Y-%m-%d'`
DATETIME=`date '+%Y-%m-%d-%H%M%S'`
APP_DIR=/home/opc/oci-usage
APPLOG_DIR=${APP_DIR}/logs

OCI_PROFILE="DEFAULT"

CSV_DIR=${APP_DIR}/oci-usage-$OCI_PROFILE

mkdir -p ${APPLOG_DIR}
mkdir -p ${CSV_DIR}

##################################
# Run Report
##################################
OUTPUT_FILE=${APPLOG_DIR}/${DATETIME}_getUsageReportsOCI.log

echo "###################################################################################"
echo "# Start running getUsageReportsOCI at `date`"
echo "###################################################################################"
echo "Please Wait ..."

python3 $APP_DIR/getUsageReportsOCI.py --ociProfile $OCI_PROFILE --destDir $CSV_DIR --targetDate $DATE > $OUTPUT_FILE 2>&1

echo "Uncompressing files, without overwrite if file exists already ..."
yes n | gunzip $CSV_DIR/*.gz

rm $CSV_DIR/*.gz
