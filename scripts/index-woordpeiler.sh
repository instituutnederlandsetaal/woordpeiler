#!/bin/bash
set -o errexit # Exit on error (set -e)

# remove the previous output and run the frequency tool
WOORDPEILER_INPUT=/vol2/blacklab-indices/chn-intern/ # should this be vol1?
WOORDPEILER_DIR=/vol1/blacklab-util/FrequencyTool/
WOORDPEILER_OUTPUT="$WOORDPEILER_DIR/tmp/" # currently defaults to tmp/
WOORDPEILER_CONFIG="$WOORDPEILER_DIR/unigram.yaml" # only index unigrams for now
rm -rf $WOORDPEILER_OUTPUT
java -Xmx48G -cp "$WOORDPEILER_DIR/blacklab-tools.jar:lib/*" nl.inl.blacklab.tools.frequency.FrequencyTool --no-merge $WOORDPEILER_INPUT $WOORDPEILER_CONFIG $WOORDPEILER_DIR

# copy the results to the woordpeiler servers and create databases
WOORDPEILER_DEV=corpustrends.dev.ivdnt.loc # will later be svowwr01.ivdnt.loc
WOORDPEILER_PROD=svatwr01.ivdnt.loc # will later be svprwr01.ivdnt.loc
WOORDPEILER_DEST=/vol1/tsv/
./update-woordpeiler-server.sh $WOORDPEILER_OUTPUT $WOORDPEILER_DEV $WOORDPEILER_DEST
./update-woordpeiler-server.sh $WOORDPEILER_OUTPUT $WOORDPEILER_PROD $WOORDPEILER_DEST
