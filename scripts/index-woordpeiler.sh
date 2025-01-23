#!/bin/bash
set -o errexit # Exit on error (set -e)

# remove the previous output and run the frequency tool
WOORDPEILER_INPUT=/vol2/blacklab-indices/chn-intern/
WOORDPEILER_DIR=/vol1/blacklab-util/FrequencyTool/
WOORDPEILER_OUTPUT="$WOORDPEILER_DIR/tmp/" # currently defaults to tmp/
WOORDPEILER_CONFIG="$WOORDPEILER_DIR/unigram.yaml" # only index unigrams for now
rm -rf $WOORDPEILER_OUTPUT
java -Xmx48G -cp "$WOORDPEILER_DIR/blacklab-tools.jar:lib/*" nl.inl.blacklab.tools.frequency.FrequencyTool --no-merge $WOORDPEILER_INPUT $WOORDPEILER_CONFIG $WOORDPEILER_DIR

# rsync the results to the woordpeiler servers
WOORDPEILER_DEV=corpustrends.dev.ivdnt.loc
WOORDPEILER_PROD=svprwr01.ivdnt.loc
WOORDPEILER_DEST=/vol1/tsv/
rsync -avz --checksum --delete $WOORDPEILER_OUTPUT $WOORDPEILER_DEV:$WOORDPEILER_DEST
rsync -avz --checksum --delete $WOORDPEILER_OUTPUT $WOORDPEILER_PROD:$WOORDPEILER_DEST
