# Day 76
Another quick query today. Given the 2 kickoff return TDs in the Pats vs. Bills game earlier today, I wanted to see how many other games had 2+ kickoff return TDs. Did any team have 3? Or 3 in a single game?  

Luckily I have an easy way to query this data using the table, `pbp_score_summary`. The code to create this table can be found `transformations.py`.

## Query
```sql
SELECT
    game_id
    ,team
    ,pbp_score AS score
FROM pbp_score_summary
WHERE tot_ret_tds >= 2
;
```

## Result
| game_id         | team | score |
| :-------------- | :--- | :---- |
| 2007_17_JAX_HOU | HOU  | 42.0  |
| 2010_03_SD_SEA  | SEA  | 27.0  |
| 2002_01_NYJ_BUF | NYJ  | 37.0  |
| 2006_14_CHI_STL | CHI  | 42.0  |
| 2009_08_MIA_NYJ | MIA  | 30.0  |
| 2009_15_CLE_KC  | CLE  | 41.0  |

Only 6 games (not including today's game) since 1999 had at least 1 team score two kickoff return TDs.  

Is there any game where there were 3 kickoff return TDs?

```sql
SELECT game_id
FROM pbp_score_summary
GROUP BY game_id
HAVING SUM(tot_ret_tds) >= 3
;
```

This query returns no results. So no games in the past 23 years had more than 2 kickoff return TDs.