# woordpeiler
Time-based trends of words using the newspaper part of Corpus Hedendaags Nederlands.

# Project environment variables
Create a `.env` with:
```sh
# db config
POSTGRES_DB=woordpeiler
POSTGRES_HOST=localhost
POSTGRES_PORT=127.0.0.1:5432 # local ip forces docker not to expose to outside
# builder also needs a port other than POSTGRES_PORT
BUILDER_PORT=127.0.0.1:5433 # local ip forces docker not to expose to outside
# user with write access, used by builder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[fill in]
# user with read access, used by server
READER_USER=reader
READER_PASSWORD=[fill in]
# docker image tag for server and client
VERSION_LABEL=dev
# server settings
INTERNAL=[true | false]
# proxy settings
PROXY_PORT=80
# client settings
CLIENT_CONFIG=[fill in] # folder with config.json and assets
```

Because we want to rotate the database docker volume every week, we use separate .env files the database and builder that can be editted programatically.
We create them by `cat`'ing the .env and appending a BUILDER_VOLUME or DATABASE_VOLUME variable with the correct volume name, pointing to that week's data.
For development you could do the same once and update them only when needed. So:

.builder.env:
```sh
# [copy over everything from .env]

# docker volume name
BUILDER_VOLUME="woordpeiler-[YYYY-MM-DD]"
```

.database.env:
```sh
# [copy over everything from .env]

# docker volume name
DATABASE_VOLUME="woordpeiler-[YYYY-MM-DD]"
```

# How to develop
A vscode workspace is available: `.code-workspace`.
Debug configurations for client & server are available: `client/.vscode`, `server/.vscode`.

## Client
First install node + npm. See `client/Dockerfile` for the version.

`cd ./client`, `npm install`, `npm run dev`, go to `http://localhost:5173`.

## Server
First install python. See `server/Dockerfile` for the version

`cd ./server`, `python -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`, `fastapi dev`, go to `http://localhost:8000`. Go to `http://localhost:8000/docs` for the docs.

## Database
First install docker (the database will be a psql container + docker volume) and python (for all kinds of insertion scripts). We use the same python version as the server.
Fill in `.env`, `.builder.env`, and `.database.env`!

`cd ./database`, `python -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`, 

Next, see `database/readme.md`.

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
