#!/bin/bash
set -o errexit # Exit on error (set -e)

TSVDATA=/vol1/tsv/
TODAY=`date +"%Y-%m-%d"` # database version control

cd /vol1/woordpeiler

# get a list of existing docker volumes and remove the oldest one
docker volume ls | grep woordpeiler | awk '{print $2}' | sort | head -n -1 | xargs docker volume rm

# set new docker volume
cat .env > .builder.env # base settings
echo "BUILDER_VOLUME=woordpeiler-$TODAY" >> .builder.env
# start up psql container
docker compose --env-file=.builder.env up builder -d --wait

# execute builder script: inserts $DEST tsv data into the psql builder container
source database/venv/bin/activate
python -m database $TSVDATA unigram 1
python -m database $TSVDATA bigram 2

# script finished. Database is ready to use in production
# down builder
docker compose down builder

# switch around volumes and up it
cat .env > .database.env # base settings
echo "DATABASE_VOLUME=woordpeiler-$TODAY" >> .database.env
docker compose --env-file=.database.env up database -d
