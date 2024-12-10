# Database Schema
## Primary tables
These tables contain the primary data. All other tables are derivates of these tables. These tables are directly updated by the data-update.

(Well... csv/tsv data first goes into a table `data_tmp`, from which words and sources are then constructed/updated. Then, frequencies is updated, as it needs the word_id and sources_id keys. But yes, these are the primary data tables)

#### frequencies
  Column   |           Type           |
-----------+--------------------------+
time      | timestamp with time zone |
word_id   | integer                  |
source_id | integer                  |
frequency | integer                  |

#### words
  Column  |  Type   |
----------+---------+
wordform | text    |
lemma    | text    |
pos      | text    |
poshead  | text    |
id       | integer |

#### sources
  Column  |  Type   |
----------+---------+
source   | text    |
language | text    |
id       | integer |

## Secondary tables
### "cache" tables
These serve one purpose: a `SELECT * FROM table` is equivalent to calculating DISTINCT/GROUP BY on some table. But calculating DISTINCT/GROUP BY is expensive, so instead we have these small tables to "cache" the result.
#### posheads
 Column  | Type |
---------+------+
 poshead | text |

#### posses
 Column | Type |
--------+------+
 pos    | text |

#### corpus size
Corpus size per day (at the lowest granularity).

 Column |           Type           |
--------+--------------------------+
 time   | timestamp with time zone |
 size   | bigint                   |

### Trend tables (enriched)
#### daily_counts
Equivalent to `frequencies` but words are no longer split by source, only by language.

daily_counts
   Column    |           Type           |
-------------+--------------------------+
 time        | timestamp with time zone |
 word_id     | integer                  |
 abs_freq    | bigint                   |
 abs_freq_an | bigint                   |
 abs_freq_bn | bigint                   |
 abs_freq_nn | bigint                   |
 abs_freq_sn | bigint                   |

 #### monthly_counts
 idem

 #### yearly_counts
 idem

 #### total_counts
  Column  |       Type       |
----------+------------------+
 word_id  | integer          |
 abs_freq | numeric          |
 rel_freq | double precision |

 ### Trend tables (unenriched)