#!/bin/bash
set -o errexit # Exit on error (set -e)

# remove the previous output
WOORDPEILER_OUTPUT=/vol1/blacklab-util/FrequencyTool/tmp/
rm -rf WOORDPEILER_OUTPUT
# run the frequency tool
/vol1/blacklab-util/FrequencyTool/calc-woordpeiler.sh

# copy the results to the woordpeiler servers and create databases
WOORDPEILER_DEV=svowct01.ivdnt.loc # will later be svowwr01.ivdnt.loc
WOORDPEILER_PROD=svatwr01.ivdnt.loc # will later be svprwr01.ivdnt.loc
WOORDPEILER_DEST=/vol1/tsv/
./update-woordpeiler-server.sh $WOORDPEILER_OUTPUT $WOORDPEILER_DEV $WOORDPEILER_DEST
./update-woordpeiler-server.sh $WOORDPEILER_OUTPUT $WOORDPEILER_PROD $WOORDPEILER_DEST
