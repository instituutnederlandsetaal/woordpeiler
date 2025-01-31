# Initialisating/updating the database
Because this project is designed to be updated weekly while the database from the previous week is still running, we have two psql docker containers.
The 'production' container is called `database`. The other, used to prepare next weeks data, is called `databuilder`. They are identical psql containers in every regard, other than that they point to a different docker volume.

Let's start with the `databuilder` container:
1. Fill in the `.env.databuilder`. (See readme.md at the root.)
2. `docker compose --env-file=.env.databuilder up databuilder -d`
3. `source database/venv/bin/activate && python -m database MY-DATA-DIR`

`MY-DATA-DIR` is a folder that contains `.tsv.gz` files. Each files contains the following columns in order:
- lemma: string
- wordform: string
- pos: string
- date: string in the form "YYYYMMDD" e.g. "20250101"
- source: string
- language: string
- frequency: integer

Example (with fake tabs):
```tsv
kat \t katten \t nou-c(gender=f|m,number=sg) \t 20220326 \t Het Nieuwsblad \t BN \t 21
hond \t honden \t nou-c(gender=f|m,number=sg) \t 20231203 \t Het Nieuwsblad \t BN \t 16
```


At this point the new database for next week has been initialised. `docker compose down databuilder`.
Now, edit `.env.database` to point to the new volume and (re)launch the `database` container: `docker compose --env-file=.env.database up database -d`.

Done!
