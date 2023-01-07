# Day 74
Today is a direct continuation of yesterday's work where I calculated the winning streak of Super Bowl winners from 1999-2020. For today I'm going to slightly tweak the query by using `game_type` in order to capture the 2021 season since that season went to 18 regular-season games instead of the usual 17 games.

## Query

```sql
WITH sb_winners AS (
    SELECT
        season,
        CASE
            WHEN result < 0 THEN away_team
            ELSE home_team
        END AS sb_winner
    FROM schedules
    WHERE game_type = 'SB'
        and season < 2022
)
SELECT
    sb_winners.season,
    sb_winner,
    start_of_winning_streak,
    current_winning_streak
FROM sb_winners
LEFT JOIN (
    WITH data_table AS
    -- Use subqueries to go from game level to game-team level
    -- Two rows per game
    (
        SELECT
            season
            ,game_id
            ,week
            ,home_team AS team
            ,home_team
            ,away_team
            ,result
        FROM schedules
        WHERE game_type = 'REG'
            AND season < 2022
        UNION ALL
        SELECT
            season
            ,game_id
            ,week
            ,away_team AS team
            ,home_team
            ,away_team
            ,result
        FROM schedules
        WHERE game_type = 'REG'
            AND season < 2022
        -- ORDER BY game_id 
    ), summary_table AS (
    SELECT
        *
        ,SUM(CASE WHEN week < start_of_losing_streak THEN NULL ELSE 1 END)
            OVER (PARTITION BY season, team
                ORDER BY week
                ROWS UNBOUNDED PRECEDING) AS current_losing_streak
        ,SUM(CASE WHEN week < start_of_winning_streak THEN NULL ELSE 1 END)
            OVER (PARTITION BY season, team
                ORDER BY week
                ROWS UNBOUNDED PRECEDING) AS current_winning_streak
    FROM (
        SELECT  *
                -- Get the week where win_flag changes
            ,MAX(CASE WHEN win_flag = 'win' THEN week+1 END) OVER(PARTITION BY season, team) AS start_of_losing_streak
            ,MAX(CASE WHEN win_flag = 'loss' THEN week+1 END) OVER(PARTITION BY season, team) AS start_of_winning_streak
        FROM (
            -- Create win/loss flag
            SELECT  
                season
                ,team
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
            ORDER BY season, team, week 
        )
    )
    ORDER BY season, team, week
    )
    SELECT  
        season
        ,team
        ,start_of_winning_streak
        ,current_winning_streak
    FROM
    (
        SELECT  
            season
            ,team
            ,start_of_winning_streak
            ,current_winning_streak
            ,MAX(current_winning_streak) OVER(PARTITION BY season, team) AS max_streak
        FROM summary_table
    )
    WHERE current_winning_streak = max_streak
    AND max_streak >= 1
    ORDER BY max_streak DESC
) t ON t.season = sb_winners.season
    AND t.team = sb_winners.sb_winner
;
```

## Result
| season | sb_winner | start_of_winning_streak | current_winning_streak |
| :----- | :-------- | :---------------------- | :--------------------- |
| 1999   | STL       | NULL                    | NULL                   |
| 2000   | BAL       | 10                      | 7                      |
| 2001   | NE        | 11                      | 6                      |
| 2002   | TB        | 17                      | 1                      |
| 2003   | NE        | 5                       | 12                     |
| 2004   | NE        | 16                      | 2                      |
| 2005   | PIT       | 14                      | 4                      |
| 2006   | IND       | 17                      | 1                      |
| 2007   | NYG       | NULL                    | NULL                   |
| 2008   | PIT       | 17                      | 1                      |
| 2009   | NO        | NULL                    | NULL                   |
| 2010   | GB        | 16                      | 2                      |
| 2011   | NYG       | 16                      | 2                      |
| 2012   | BAL       | NULL                    | NULL                   |
| 2013   | SEA       | 17                      | 1                      |
| 2014   | NE        | NULL                    | NULL                   |
| 2015   | DEN       | 16                      | 2                      |
| 2016   | NE        | 11                      | 7                      |
| 2017   | PHI       | NULL                    | NULL                   |
| 2018   | NE        | 16                      | 2                      |
| 2019   | KC        | 11                      | 6                      |
| 2020   | TB        | 13                      | 4                      |
| 2021   | LA        | NULL                    | NULL                   |

**Note**: NULL values mean that the team **lost** the last game of the regular season.  

The LA Rams from 2021 was another example of a SB winning team who lost their last game. Interestingly enough it was against the San Francisco who they ended up beating in the NFC Championship game.