# Day 53
Today I wanted to try something a little different. Since I want to practice more in SQL and show my work, I am going to utilize `Markdown` to write today's post, placing the SQL code into code blocks and then converting the result sets into markdown tables. I think the result will be a much cleaner post and will give readers a chance to better understand the SQL.  

All of this is done using VS Code and different extensions. The data is courtesy of [nflverse](https://nflverse.nflverse.com) and the code to create the database I am using for today's post can be found in `root/etl/`.

## Top 5 And Bottom 5 Teams by Percentage of Pass Yards After Catch
I wanted to see which teams rely more (or less) on YAC (yards after catch) to get their passing yards.

### Query
```sql
SELECT  *
FROM
(
	SELECT  *
	       ,RANK() OVER(ORDER BY pct_yac DESC) AS rank_pct_yac
	FROM
	(
		SELECT  recent_team                                                                AS team
		       ,SUM(passing_yards)                                                         AS total_pass_yards
		       ,SUM(passing_yards_after_catch)                                             AS total_pass_yac
		       ,ROUND((1.0 * SUM(passing_yards_after_catch) / SUM(passing_yards)) * 100,2) AS pct_yac
		FROM weekly
		WHERE season = 2022
		    AND week <= 14
		    AND position = 'QB'
		GROUP BY  recent_team
	) AS aggregation
) AS rankings
WHERE rank_pct_yac <= 5 OR rank_pct_yac >= 28;
```

### Result
| team | total_pass_yards | total_pass_yac | pct_yac | rank_pct_yac |
| :--- | :--------------- | :------------- | :------ | :----------- |
| CAR  | 2387.0           | 1354.0         | 56.72   | 1            |
| SF   | 3102.0           | 1731.0         | 55.8    | 2            |
| LAC  | 3706.0           | 2017.0         | 54.43   | 3            |
| HOU  | 2773.0           | 1472.0         | 53.08   | 4            |
| KC   | 4160.0           | 2199.0         | 52.86   | 5            |
| ATL  | 2219.0           | 900.0          | 40.56   | 28           |
| BUF  | 3561.0           | 1410.0         | 39.6    | 29           |
| PIT  | 2870.0           | 1127.0         | 39.27   | 30           |
| NO   | 3110.0           | 1198.0         | 38.52   | 31           |
| MIA  | 3804.0           | 1415.0         | 37.2    | 32           |

I was a little surprised to see Carolina at #1. This could be due to them ranking 30th in total passing yards but heavily relying on a player like Christian McCaffrey who is known for high YAC. One way to see if my hunch is correct would be to look at Carolina's `pct_yac` when they had Christian McCaffrey (Weeks 1-6) and their `pct_yac` after they traded him away to San Francisco.

## Top 5 Teams by Percentage of Pass Yards After Catch (Weeks 1-6)

### Query
```sql
SELECT  *
FROM
(
	SELECT  *
	       ,RANK() OVER(ORDER BY pct_yac DESC) AS rank_pct_yac
	FROM
	(
		SELECT  recent_team                                                                AS team
		       ,SUM(passing_yards)                                                         AS total_pass_yards
		       ,SUM(passing_yards_after_catch)                                             AS total_pass_yac
		       ,ROUND((1.0 * SUM(passing_yards_after_catch) / SUM(passing_yards)) * 100,2) AS pct_yac
		FROM weekly
		WHERE season = 2022
		AND week <= 6
		AND position = 'QB'
		GROUP BY  recent_team
	) AS aggregation
) AS rankings
WHERE rank_pct_yac <= 5 OR rank_pct_yac >= 28;
```

### Result
| team | total_pass_yards | total_pass_yac | pct_yac | rank_pct_yac |
| :--- | :--------------- | :------------- | :------ | :----------- |
| CAR  | 1141.0           | 721.0          | 63.19   | 1            |
| SF   | 1347.0           | 799.0          | 59.32   | 2            |
| GB   | 1476.0           | 860.0          | 58.27   | 3            |
| CIN  | 1616.0           | 913.0          | 56.5    | 4            |
| LA   | 1576.0           | 890.0          | 56.47   | 5            |

Bingo. Carolina is the number 1 team by `pct_yac` and it isn't particularly close. For good measure I'll get the top teams for Weeks 7-14.

## Top Teams by Percentage of Pass Yards After Catch (Weeks 7-14)

### Query
```sql
SELECT  *
FROM
(
	SELECT  *
	       ,RANK() OVER(ORDER BY pct_yac DESC) AS rank_pct_yac
	FROM
	(
		SELECT  recent_team                                                                AS team
		       ,SUM(passing_yards)                                                         AS total_pass_yards
		       ,SUM(passing_yards_after_catch)                                             AS total_pass_yac
		       ,ROUND((1.0 * SUM(passing_yards_after_catch) / SUM(passing_yards)) * 100,2) AS pct_yac
		FROM weekly
		WHERE season = 2022
		AND week BETWEEN 7 AND 14
		AND position = 'QB'
		GROUP BY  recent_team
	) AS aggregation
) AS rankings
WHERE rank_pct_yac <= 5 OR rank_pct_yac >= 28;
```

### Result
| team | total_pass_yards | total_pass_yac | pct_yac | rank_pct_yac |
| :--- | :--------------- | :------------- | :------ | :----------- |
| HOU  | 1725.0           | 991.0          | 57.45   | 1            |
| NE   | 1597.0           | 913.0          | 57.17   | 2            |
| LAC  | 1990.0           | 1092.0         | 54.87   | 3            |
| DET  | 1997.0           | 1073.0         | 53.73   | 4            |
| SF   | 1755.0           | 932.0          | 53.11   | 5            |
| NYJ  | 1660.0           | 874.0          | 52.65   | 6            |
| KC   | 2424.0           | 1270.0         | 52.39   | 7            |
| DEN  | 1604.0           | 834.0          | 52.0    | 8            |
| CAR  | 1246.0           | 633.0          | 50.8    | 9            |
| NYG  | 1560.0           | 781.0          | 50.06   | 10           |

After trading away Christian McCaffrey, Carolina dropped to 10th in `pct_yac`; from 63% of passing yards coming after the catch to just 50%. That's quite a decrease!