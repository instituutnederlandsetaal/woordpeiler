# [Woordpeiler](https://woordpeiler.ivdnt.org)
Woordpeiler provides corpus-based temporal word frequencies and trend analysis. It consists of a Vue 3 + D3.js frontend, a Python FastAPI backend, a PostgreSQL/TimescaleDB database, and nginx proxy. Data is provided via a [BlackLab](https://github.com/instituutnederlandsetaal/blacklab) corpus, specifically via the BlackLab FrequencyTool.

## Team
- Principal engineer: Vincent Prins (vincent.prins@ivdnt.org)
- Scientific advisor: Kris Heylen

# Development
A vscode workspace is available: `.code-workspace`.
Debug configurations for client & server are available: `client/.vscode`, `server/.vscode`.
Development requires a .env. Depending on you setup, you might have to copy over the .env to the respective subfolders.

## .env
```sh
# db config
POSTGRES_DB=woordpeiler
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
# builder also needs a port other than POSTGRES_PORT
BUILDER_PORT=5433
# user with write access, used by builder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[fill in]
# user with read access, used by server
READER_USER=reader
READER_PASSWORD=[fill in]
# docker image tag for server and client
VERSION=[dev | x.x.x]
# server settings
INTERNAL=[true | false]
# proxy settings
PROXY_PORT=80
# client settings folder with config.json and assets
CLIENT_CONFIG=[fill in]
# database docker volume name
DATABASE_VOLUME=[fill in]
```

## Client
- Install node + npm (e.g. via [nvm](https://github.com/nvm-sh/nvm)). See `client/Dockerfile` for the version.
- `cd client`
- `npm i`
- `npm run dev`, go to `http://localhost:5173`.

## Server
- Install python (e.g. via [uv](https://github.com/astral-sh/uv)). See `server/Dockerfile` for the version
- `cd server`
- `python -m venv .venv` (or `uv venv`)
- `source .venv/bin/activate`
- `pip install -r requirements.txt` (or `uv pip [...]`)
- `fastapi dev`, go to `http://localhost:8000`. Go to `http://localhost:8000/docs` for the docs.

## Database
- Install docker, psql and python (see above). The python version matches the server.
- `cd database`, 
- `python -m venv venv`, 
- `source venv/bin/activate`, 
- `pip install -r requirements.txt`
- For database creation, see `database/readme.md`.

## Testing
### Load tests
- Install locust (`pip install locust`) either globally or create a venv.
- `cd server/tests/load_tests`
- `locust`, go to `http://localhost:8089/`

# Deployment
- Install docker. 
- `git clone https://github.com/instituutnederlandsetaal/woordpeiler`
- `cd woordpeiler`.
- Fill in the `.env`.
- For database creation, see `database/readme.md`.
- `docker compose up -d --force-recreate proxy` 
    - docker compose "depends_on" will up the rest.
    - "force-recreate" will clear any cache.

## Docker images
Docker images are available on Docker Hub.
- [instituutnederlandsetaal/woordpeiler-server](https://hub.docker.com/repository/docker/instituutnederlandsetaal/woordpeiler-server)
- [instituutnederlandsetaal/woordpeiler-client](https://hub.docker.com/repository/docker/instituutnederlandsetaal/woordpeiler-client)
