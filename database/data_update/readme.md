# CorpusTrends Data Update

`python3 -m database.data_update.insert [YYYYMMDD] [data_dir]` will:
- create a table `data_tmp` if it doesn't exist
- download the data for that day with curl from blacklab server into a csv file (save in `data_dir`)
- insert it into table `data_tmp`

`python3 -m database.data_update.update` will:
- update the `words` and `sources` table with the new words and sources in `data_tmp`
- update the `frequencies` table with the datapoints in `data_tmp`
- drop table `data_tmp`

`python3 -m database.data_update.lookup_tables` will:
- construct table `corpus_size`
- create `daily_counts`, `monthly_counts`, `yearly_counts` and `total_counts` from `frequencies`
- drop `frequency_tmp`

`python3 -m database.data_update` will:
- do all of the above for the date range: [last date in database, now]
