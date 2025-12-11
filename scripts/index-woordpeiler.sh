#!/bin/bash
set -o errexit # Exit on error (set -e)

#####################
# Frequency Tool
#####################
WOORDPEILER_INPUT=/vol2/blacklab-indices/chn-intern/
WOORDPEILER_DIR=/vol1/blacklab-util/FrequencyTool/
WOORDPEILER_OUTPUT="$WOORDPEILER_DIR/output/"
WOORDPEILER_CONFIG="$WOORDPEILER_DIR/woordpeiler.yaml"

# remove previous output and recreate dir
rm -rf $WOORDPEILER_OUTPUT
mkdir -p $WOORDPEILER_OUTPUT
# run frequency tool
java -Xmx48G -cp "$WOORDPEILER_DIR/blacklab-tools.jar:lib/*" nl.inl.blacklab.tools.frequency.FrequencyTool $WOORDPEILER_INPUT $WOORDPEILER_CONFIG $WOORDPEILER_OUTPUT

#####################
# Deploy
#####################
WOORDPEILER_DEV=woordpeiler.dev.ivdnt.loc
WOORDPEILER_PROD=woordpeiler.ivdnt.org
WOORDPEILER_DEST=/vol1/tsv/
WOORDPEILER_SCRIPT=/vol1/woordpeiler/scripts/create-database.sh

# rsync to woordpeiler servers
rsync -avz --checksum --delete $WOORDPEILER_OUTPUT $WOORDPEILER_DEV:$WOORDPEILER_DEST
rsync -avz --checksum --delete $WOORDPEILER_OUTPUT $WOORDPEILER_PROD:$WOORDPEILER_DEST
# run script on target server (background job, will quit immediately)
ssh $WOORDPEILER_DEV "cd /vol1/woordpeiler/ && $WOORDPEILER_SCRIPT"
ssh $WOORDPEILER_PROD "cd /vol1/woordpeiler/ && $WOORDPEILER_SCRIPT"
