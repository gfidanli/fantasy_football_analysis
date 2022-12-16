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

I was a little surprised to see Carolina at #1. This could be due to them ranking 30th in total passing yards but heavily relying on a player like Christian McCaffrey who is known for high YAC.
