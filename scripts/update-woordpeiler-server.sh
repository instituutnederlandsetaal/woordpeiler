#!/bin/bash
set -o errexit # Exit on error (set -e)

TSVDATA=/vol1/tsv/
TODAY=`date +"%Y-%m-%d"` # database version control

cd /vol1/woordpeiler

# get a list of existing docker volumes and remove the oldest one
docker volume ls | grep woordpeiler | awk '{print $2}' | sort | head -n -1 | xargs docker volume rm

# set new docker volume
cat .env > .env.databuilder # base settings
echo "DATABUILDER_VOLUME=woordpeiler-$TODAY" >> .env.databuilder

# start up psql container
docker compose --env-file=.env.databuilder up databuilder -d --wait

# execute databuilder script: inserts $DEST tsv data into the psql databuilder container
source database/venv/bin/activate
python -m database $TSVDATA

# script finished. Database is ready to use in production
# down databuilder
docker compose down databuilder

# switch around volumes and up it
cat .env > .env.database # base settings
echo "DATABASE_VOLUME=woordpeiler-$TODAY" >> .env.database
docker compose --env-file=.env.database up database -d
