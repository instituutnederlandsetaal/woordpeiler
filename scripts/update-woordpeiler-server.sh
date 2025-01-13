#!/bin/bash
set -o errexit # Exit on error (set -e)

if [ -z "$1" ]; then
    echo "Specify source to copy from."
    exit 1
fi
if [ -z "$2" ]; then
    echo "Specify server to copy to."
    exit 1
fi
if [ -z "$3" ]; then
    echo "Specify destination to copy to."
    exit 1
fi

# Vars
SOURCE=$1
SERVER=$2
DEST=$3
DATE=`date +"%Y-%m-%d"` # database version control

# Copy
rsync -avz --checksum --delete $SOURCE $SERVER:$DEST
# Create database on server in a separate docker volume and container, so the old version keeps running.
ssh $SERVER "
	cd /vol1/woordpeiler && \
	
	# set docker volume
	cat .env > .env.databuilder && \ # base settings
	echo "DATABUILDER_VOLUME=woordpeiler-$DATE" >> .env.databuilder && \
	
	# start up psql container
	docker compose --env-file=.env.databuilder up databuilder -d && \
	
	# execute databuilder script: inserts $DEST tsv data into the psql databuilder container
	source database/venv/bin/activate && \
	python -m database.initialize $DEST && \
	
	# script finished. Database is ready to use in production
	# down databuilder
	docker compose down databuilder && \
	
	# switch around volumes and up it
	cat .env > .env.database && \ # base settings
	echo "DATABASE_VOLUME=woordpeiler-$DATE" >> .env.database && \
	docker compose --env-file=.env.database up database -d
"