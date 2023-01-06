# Day 73
With the NFL Playoffs fast approaching I wanted to utilize my query that shows a team's winning streak as of a given week and adapt it to report the SuperBowl winning team's win streak as of the last week of the regular season. I want to gain some insight on how momentum may or may not play a factor coming into the playoffs. I was able to go back to 1999 and report out who won the SuperBowl that season and how well they ended the regular season. The results may surprise you...

**Note**: I'm leaving out 2021 because I didn't have time to adjust my query to account for the extra week (18 vs 17). Will update the code as part of another day's work.

## Query
The first step is to get each team that won the SuperBowl (2021-1999)

```sql
SELECT
    season,
    CASE
        WHEN result < 0 THEN away_team
        ELSE home_team
    END AS sb_winner
FROM schedules
WHERE game_type = 'SB'
;
```

Now I just combine that with the query that I wrote in a previous day's work...

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
        and season < 2021
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
        SELECT  *
        FROM
        (
            SELECT  away_team AS team
                ,*
            FROM schedules
            WHERE season < 2021
            AND week <= 17
        ) AS home_teams
        UNION ALL
        SELECT  *
        FROM
        (
            SELECT  home_team AS team
                ,*
            FROM schedules
            WHERE season < 2021
            AND week <= 17 
        ) AS home_teams
        ORDER BY game_id 
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

**Note**: NULL values mean that the team **lost** the last game of the regular season.  

So while we see some Super Bowl winning teams who entered the postseason on 4, 6, 7 even 12-game winning streaks, the majority of these championship teams entered the postseason with 1-2 consecutive wins or even a loss! Take the New York Giants in 2007. They actually lost to the dominant 16-0 Patriots in Week 17 but wound up beating them in the Super Bowl that year!  

These findings are interesting but don't tell the whole story. For instance, if a team is good enough to win the Super Bowl, there's a good chance they didn't need to win their last regular season game to make it to the playoffs and might have rested their players, causing them to lose their last regular season game. A better way to determine momentum might be to get the last month or second half of the regular season winning percentage or defensive performance.