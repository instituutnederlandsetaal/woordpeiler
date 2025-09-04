#!/bin/bash
set -e # Exit on error

TSV_DIR=/vol1/tsv/
ENV_FILE=".env"
TODAY=`date +"%Y-%m-%d"` # database version control
CURRENT_DIR=`basename $PWD`
BUILDER_VOLUME="$CURRENT_DIR-$TODAY"

# terminal colours
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# print usage when too many arguments are given
# or when -h or --help is given
if [ "$#" -gt 2 ] || [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [TSV_DIR] [ENV_FILE]"
    echo "    - TSV_DIR: defaults to /vol1/tsv/"
    echo "    - ENV_FILE: defaults to .env"
    exit 0
fi

# if the first argument is given, use it as TSV_DIR
if [ -n "$1" ]; then
    TSV_DIR="$1"
fi

# if the second argument is given, use it as ENV_FILE
if [ -n "$2" ]; then
    ENV_FILE="$2"
fi

# check if the folder exists and is readable in terms of permissions
if [ ! -d "$TSV_DIR" ] || [ ! -r "$TSV_DIR" ]; then
    echo -e "${RED}Error: TSV dir '$TSV_DIR' does not exist or is not readable.${NC}"
    exit 1
fi

# check if the env file exists and is readable in terms of permissions
if [ ! -f "$ENV_FILE" ] || [ ! -r "$ENV_FILE" ]; then
    echo "Error: ENV file '$ENV_FILE' does not exist or is not readable."
    exit 1
fi

# check if builder is already running by running docker compose exec builder
if [[ `docker compose ps -q builder 2>/dev/null` != "" ]]; then
    echo -e "${RED}Error: Builder is already running.${NC}"
    echo "Remove it:"
    echo "    docker compose down builder"
    exit 1
fi
# check if the docker volume already exists
if docker volume ls | grep -q "$BUILDER_VOLUME"; then
    echo -e "${RED}Error: Docker volume '$BUILDER_VOLUME' already exists.${NC}"
    echo "Remove it:"
    echo "    docker volume rm $BUILDER_VOLUME"
    exit 1
fi

# set new docker volume
cat $ENV_FILE > .builder.env # base settings
echo "BUILDER_VOLUME=$BUILDER_VOLUME" >> .builder.env

# create log folder
mkdir -p logs

# background task
nohup bash -c "
    set -e # Exit on error
    # start up psql container
    docker compose --env-file=.builder.env up builder -d --wait 

    # insert tsv data into database
    source database/venv/bin/activate
    python -m database $TSV_DIR unigram 1
    python -m database $TSV_DIR bigram 2

    # script finished. Down builder.
    docker compose down builder
    echo "Created docker volume '$BUILDER_VOLUME'"
" > logs/$BUILDER_VOLUME.log 2>&1 &

echo -e "${GREEN}Creating database in docker volume $BUILDER_VOLUME.${NC}"
echo "Monitor progress:"
echo "    tail -f logs/$BUILDER_VOLUME.log"
