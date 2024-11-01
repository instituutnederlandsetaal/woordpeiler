# Corpustrends
Time-based trends of words using the newspaper part of Corpus Hedendaags Nederlands.

# How to develop
## Client
First install npm.

`cd client`, `npm install`, `npm run dev`

## Server
First install python 3.12

`cd server`, `python -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`, `fastapi dev app.py`

## Database
First install docker and python 3.12.
`cp .env.template .env` and fill it in.

`docker compose up database -d`, `cd database`, `python -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`, `python -m database [path_to_data_folder]` where your datafolder is filled with *.tsv.gz as created by the blacklab frequency tool.

# How to deploy
Deployment works solely with docker.
Install docker.
`cp .env.template .env` and fill it in.
`docker compose up -d`.
Or set a continuous cronjob for `scripts/deploy.sh`. 