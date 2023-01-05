# Day 72
Updating the query I wrote for Day 54 with the latest data available (through Week 17).


## Query
```sql
WITH data_table AS
-- Use subqueries to go from game level to game-team level
-- Two rows per game
(
	SELECT  *
	FROM
	(
		SELECT  away_team AS team
		       ,*
		FROM schedules
		WHERE season = 2022
		AND week <= 17 
	) AS home_teams
	UNION ALL
	SELECT  *
	FROM
	(
		SELECT  home_team AS team
		       ,*
		FROM schedules
		WHERE season = 2022
		AND week <= 17 
	) AS home_teams
	ORDER BY game_id 
), summary_table AS (
SELECT
    *
    ,SUM(CASE WHEN week < start_of_losing_streak THEN NULL ELSE 1 END)
        OVER (PARTITION BY team
              ORDER BY week
              ROWS UNBOUNDED PRECEDING) AS current_losing_streak
    ,SUM(CASE WHEN week < start_of_winning_streak THEN NULL ELSE 1 END)
        OVER (PARTITION BY team
              ORDER BY week
              ROWS UNBOUNDED PRECEDING) AS current_winning_streak
FROM (
	SELECT  *
            -- Get the week where win_flag changes
	       ,MAX(CASE WHEN win_flag = 'win' THEN week+1 END) OVER(PARTITION BY team) AS start_of_losing_streak
           ,MAX(CASE WHEN win_flag = 'loss' THEN week+1 END) OVER(PARTITION BY team) AS start_of_winning_streak
    FROM (
        -- Create win/loss flag
        SELECT  team
            ,game_id
            ,week
            ,home_team
            ,away_team
            ,result,
            CASE
                WHEN team = home_team AND result > 0 THEN 'win'
                WHEN team <> home_team AND result < 0 THEN 'win'
                WHEN result = 0 THEN 'draw'
                ELSE 'loss'
            END AS win_flag
        FROM data_table
        ORDER BY team, week 
    )
)
ORDER BY team, week
)
SELECT  team
       ,start_of_losing_streak
       ,current_losing_streak
FROM
(
	SELECT  team
	       ,start_of_losing_streak
	       ,current_losing_streak
	       ,MAX(current_losing_streak) OVER(PARTITION BY team) AS max_streak
	FROM summary_table
)
WHERE current_losing_streak = max_streak
AND max_streak > 1
ORDER BY max_streak DESC
;
```

## Result
| team | start_of_losing_streak | current_losing_streak |
| :--- | :--------------------- | :-------------------- |
| CHI  | 8                      | 9                     |
| ARI  | 11                     | 6                     |
| IND  | 11                     | 6                     |
| TEN  | 12                     | 6                     |
| MIA  | 13                     | 5                     |
| NYJ  | 13                     | 5                     |
| WAS  | 13                     | 4                     |
| DEN  | 16                     | 2                     |
| LV   | 16                     | 2                     |
| PHI  | 16                     | 2                     |

The Chicago Bears are on a 9-game losing streak that started back on Week 8! 10 out of 32 teams are on at least a 2 game losing streak as of Week 17.  

## Winning Streaks
To see the teams on current winning streaks, simply change a few variable names in the final query:

```sql
-- Above is same as previous query
SELECT  team
       ,start_of_winning_streak
       ,current_winning_streak
FROM
(
	SELECT  team
	       ,start_of_winning_streak
	       ,current_winning_streak
	       ,MAX(current_winning_streak) OVER(PARTITION BY team) AS max_streak
	FROM summary_table
)
WHERE current_winning_streak = max_streak
AND max_streak > 1
ORDER BY max_streak DESC
;
```
The result set is:

| team | start_of_winning_streak | current_winning_streak |
| :--- | :---------------------- | :--------------------- |
| SF   | 8                       | 9                      |
| GB   | 13                      | 4                      |
| JAX  | 14                      | 4                      |
| KC   | 14                      | 4                      |
| LAC  | 14                      | 4                      |
| NO   | 14                      | 3                      |
| PIT  | 15                      | 3                      |
| DAL  | 16                      | 2                      |
| TB   | 16                      | 2                      |

San Francisco has stayed hot since the last time I ran this query. They've increased their win streak to 9 games. Green Bay and Jacksonville have been surging lately in an attempt to make the playoffs.