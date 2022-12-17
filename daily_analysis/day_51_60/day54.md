# Day 54
Today I wanted more practice with SQL so I decided to create a summary of each team and their current losing streak. It turned out top be really good practice with CTEs, nested subqueries, window functions, and case statements. 


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
		AND week <= 14 
	) AS home_teams
	UNION ALL
	SELECT  *
	FROM
	(
		SELECT  home_team AS team
		       ,*
		FROM schedules
		WHERE season = 2022
		AND week <= 14 
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
SELECT  *
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
| team | start_of_losing_streak | current_losing_streak | max_streak |
| :--- | :--------------------- | :-------------------- | :--------- |
| HOU  | 6                      | 8                     | 8          |
| CHI  | 8                      | 6                     | 6          |
| DEN  | 9                      | 5                     | 5          |
| NYG  | 11                     | 4                     | 4          |
| ARI  | 11                     | 3                     | 3          |
| IND  | 11                     | 3                     | 3          |
| TEN  | 12                     | 3                     | 3          |
| ATL  | 12                     | 2                     | 2          |
| MIA  | 13                     | 2                     | 2          |
| NO   | 12                     | 2                     | 2          |
| NYJ  | 13                     | 2                     | 2          |

The Houston Texans are on an 8-game losing streak that started back on Week 6! 11 out of 32 teams are on at least a 2 game losing streak as of Week 14.  

## Winning Streaks
To see the teams on current winning streaks, simply change a few variable names in the final query:

```sql
-- Above is same as previous query
SELECT  *
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

| team | start_of_winning_streak | current_winning_streak | max_streak |
| :--- | :---------------------- | :--------------------- | :--------- |
| SF   | 8                       | 6                      | 6          |
| CIN  | 9                       | 5                      | 5          |
| BUF  | 11                      | 4                      | 4          |
| DAL  | 11                      | 4                      | 4          |
| PHI  | 11                      | 4                      | 4          |
| WAS  | 10                      | 4                      | 4          |
| BAL  | 13                      | 2                      | 2          |
| CAR  | 12                      | 2                      | 2          |
| DET  | 13                      | 2                      | 2          |

San Francisco is the hottest team in the league right now and currently on a 6-game win streak. The Bengals are on their tail with a win streak of 5 games.