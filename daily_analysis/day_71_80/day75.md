# Day 75
It's the weekend so today will be a quick query to get the biggest blowouts by season from 1999-2022. To get the biggest blowout by season I simply take the maximum of the difference in points between the winning team and losing team and aggregate by season.

## Query
```sql
SELECT  season
       ,week
       ,game_type
       ,home_team
       ,away_team
       ,MAX(ABS(result)) AS point_diff
       ,CASE WHEN result < 0 THEN 'away win'  ELSE 'home win' END AS result
FROM schedules
WHERE game_type = 'REG'
GROUP BY  season;
```

## Result
| season | week | game_type | home_team | away_team | point_diff | result   |
| :----- | :--- | :-------- | :-------- | :-------- | :--------- | :------- |
| 1999   | 15   | REG       | OAK       | TB        | 45.0       | home win |
| 2000   | 14   | REG       | JAX       | CLE       | 48.0       | home win |
| 2001   | 17   | REG       | NO        | SF        | 38.0       | away win |
| 2002   | 13   | REG       | KC        | ARI       | 49.0       | home win |
| 2003   | 1    | REG       | SF        | CHI       | 42.0       | home win |
| 2004   | 7    | REG       | KC        | ATL       | 46.0       | home win |
| 2005   | 5    | REG       | GB        | NO        | 49.0       | home win |
| 2006   | 4    | REG       | KC        | SF        | 41.0       | home win |
| 2007   | 11   | REG       | BUF       | NE        | 46.0       | away win |
| 2008   | 10   | REG       | NYJ       | STL       | 44.0       | home win |
| 2009   | 6    | REG       | NE        | TEN       | 59.0       | home win |
| 2010   | 7    | REG       | DEN       | OAK       | 45.0       | away win |
| 2011   | 7    | REG       | NO        | IND       | 55.0       | home win |
| 2012   | 14   | REG       | SEA       | ARI       | 58.0       | home win |
| 2013   | 16   | REG       | PHI       | CHI       | 43.0       | home win |
| 2014   | 13   | REG       | STL       | OAK       | 52.0       | home win |
| 2015   | 3    | REG       | ARI       | SF        | 40.0       | home win |
| 2016   | 16   | REG       | NE        | NYJ       | 38.0       | home win |
| 2017   | 4    | REG       | HOU       | TEN       | 43.0       | home win |
| 2018   | 1    | REG       | BAL       | BUF       | 44.0       | home win |
| 2019   | 1    | REG       | MIA       | BAL       | 49.0       | away win |
| 2020   | 13   | REG       | LAC       | NE        | 45.0       | away win |
| 2021   | 16   | REG       | DAL       | WAS       | 42.0       | home win |
| 2022   | 11   | REG       | MIN       | DAL       | 37.0       | away win |

Biggest blowout in the last 23 years was when the New England Patriots beat the Tennessee Titans by 59 points at home.  

Not surprisingly, almost all of these blowouts have been by home teams which makes sense.