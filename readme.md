# woordpeiler
Time-based trends of words using the newspaper part of Corpus Hedendaags Nederlands.

# Project environment variables
Create a `.env` with:
```sh
# db config
POSTGRES_DB=woordpeiler
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
# user with write access
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[fill in]
# user with read access
READER_USER=reader
READER_PASSWORD=[fill in]
# docker volume names
DATABASE_VOLUME="woordpeiler-[date]"
DATABUILDER_VOLUME="woordpeiler-[date]"
# databuilder also needs a port other than POSTGRES_PORT
DATABUILDER_PORT=5433
# docker image tag
VERSION_LABEL=dev
```

# How to develop
A vscode workspace is available: `.code-workspace`.
Debug configurations for client & server are available: `client/.vscode`, `server/.vscode`.

## Client
First install npm. See `client/Dockerfile` for the version.

`cd ./client`, `npm install`, `npm run dev`, go to `http://localhost:5173`.

## Server
First install python. See `server/Dockerfile` for the version

`cd ./server`, `python -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`, `fastapi dev`, go to `http://localhost:8000`. Go to `http://localhost:8000/docs` for the docs.

## Database
First install docker (for the actual database, it will be a volume) and python (for all kinds of insertion scripts). We use the same python version as the server.
Fill in the `.env`! Docker compose will need it.
`docker compose up database -d`

# How to unit & load test

## unit tests (server)
For unit tests, we use the standard library `unittest` python package. If you open the vscode workspace, unit tests should be auto-discovered and appear on the sidebar. Otherwise, you can run `python -m unittest discover ./server/tests`.

## load tests (server)
For load tests we use locust. Either install this globally (`pip install locust`) or create a venv.

`cd ./server/tests/load_tests`, `locust`, go to `http://localhost:8089/`

# How to deploy
Deployment works solely with docker.
Install docker. Fill in the `.env`.
`git clone [...]`, `cd [...]`, `docker compose up -d`.
Or set a continuous cronjob for `scripts/deploy.sh`. 

# How to populate the database
See `database/readme.md`.