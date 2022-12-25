# Day 63
Merry Christmas to everyone who celebrates! Given that it's Christmas, today I'm going to reuse code from [Day 31](https://github.com/gfidanli/fantasy_football_analysis/blob/main/daily_analysis/day_31_40/day31.ipynb) to look into Christmas games since 1999 and list out some interesting facts.

## Query
```sql
-- Christmas Games
-- 3 in 2022 but will remove from analysis
WITH christmas_games AS (
    SELECT
        game_id,
        season,
        gameday,
        weekday,
        away_team,
        away_score,
        home_team,
        home_score,
        result,
        total,
        overtime
    FROM schedules
    WHERE season <= 2021
        AND strftime('%m', gameday) = '12'
        AND strftime('%d', gameday) = '25'
    ORDER BY season
), home_teams AS (
    SELECT
        game_id,
        'home' AS home_away,
        home_team AS team,
        home_score AS score,
        result,
        CASE
            WHEN result > 0 THEN 'win'
            ELSE 'lose'
        END AS win_lose,
        total,
        overtime
    FROM christmas_games
), away_teams AS (
    SELECT
        game_id,
        'away' AS home_away,
        away_team AS team,
        away_score AS score,
        result,
        CASE
            WHEN result < 0 THEN 'win'
            ELSE 'lose'
        END AS win_lose,
        total,
        overtime
    FROM christmas_games
), stacked AS (
    SELECT *
    FROM home_teams
    UNION ALL
    SELECT *
    FROM away_teams
), rankings AS (
    SELECT *,
        COUNT() OVER(PARTITION BY team) AS num_games
    FROM stacked
), summary AS (
    SELECT 
        team,
        home_away,
        win_lose,
        ROUND(AVG(result),2) AS avg_result,
        COUNT(*) AS num_wins_losses,
        ROUND(COUNT(*) * 1.0 / num_games,2) AS pct_win_lose,
        num_games 
    FROM rankings
    GROUP BY team, home_away, win_lose
    ORDER BY num_games DESC, team
)
SELECT *
FROM summary 
;
```

## Result
| team | home_away | win_lose | avg_result | num_wins_losses | pct_win_lose | num_games |
| :--- | :-------- | :------- | :--------- | :-------------- | :----------- | :-------- |
| DAL  | away      | lose     | 16.0       | 2               | 0.67         | 3         |
| DAL  | home      | lose     | -16.0      | 1               | 0.33         | 3         |
| DEN  | away      | lose     | 23.0       | 1               | 0.33         | 3         |
| DEN  | away      | win      | -15.5      | 2               | 0.67         | 3         |
| GB   | home      | lose     | -7.0       | 1               | 0.33         | 3         |
| GB   | home      | win      | 8.0        | 2               | 0.67         | 3         |
| TEN  | home      | lose     | -23.0      | 2               | 0.67         | 3         |
| TEN  | home      | win      | 31.0       | 1               | 0.33         | 3         |
| ARI  | home      | lose     | -6.0       | 1               | 0.5          | 2         |
| ARI  | home      | win      | 1.0        | 1               | 0.5          | 2         |
| BAL  | away      | lose     | 4.0        | 1               | 0.5          | 2         |
| BAL  | home      | win      | 7.0        | 1               | 0.5          | 2         |
| CHI  | away      | lose     | 14.0       | 1               | 0.5          | 2         |
| CHI  | away      | win      | -7.0       | 1               | 0.5          | 2         |
| KC   | home      | win      | 12.0       | 2               | 1.0          | 2         |
| MIN  | away      | lose     | 13.0       | 2               | 1.0          | 2         |
| OAK  | away      | lose     | 5.0        | 2               | 1.0          | 2         |
| PHI  | away      | win      | -16.0      | 1               | 0.5          | 2         |
| PHI  | home      | win      | 9.0        | 1               | 0.5          | 2         |
| PIT  | away      | win      | -28.0      | 1               | 0.5          | 2         |
| PIT  | home      | win      | 4.0        | 1               | 0.5          | 2         |
| CLE  | away      | lose     | 2.0        | 1               | 1.0          | 1         |
| DET  | home      | lose     | -10.0      | 1               | 1.0          | 1         |
| HOU  | home      | lose     | -28.0      | 1               | 1.0          | 1         |
| IND  | away      | win      | -6.0       | 1               | 1.0          | 1         |
| MIA  | home      | lose     | -3.0       | 1               | 1.0          | 1         |
| NO   | home      | win      | 19.0       | 1               | 1.0          | 1         |
| NYJ  | away      | win      | -3.0       | 1               | 1.0          | 1         |
| SD   | away      | win      | -25.0      | 1               | 1.0          | 1         |

**How to read**: Dallas has been in 3 Christmas Games since 1999. Two of the games have been away, with only one game at home. They've lost all three of those games by an average of 16 pts or by more than 2 scores. Another way to look at it is that they 67% of their Christmas games they were away and lost.  

Fun Facts (since 1999...):
1. For the teams with 3 games played, Dallas is the only one to lose every game. For the teams with 2 games played, both Minnesota and Vegas have 2 losses.
2. Kansas City is the only undefeated team (at least 2 games played)
3. Tennessee owns the highest margin of victory – 31 pts over Dallas in 2000.
4. Houston owns the worst defeat – a loss by 28 points to Pittsburgh in 2017
5. No game went to Overtime
6. By using the `christmas_games` table, you'll notice that the NFL has been having Christmas Games more recently, starting in 2016. Since 2016 (6 years) there have been 7 games with 3 scheduled for 2022. From 1999 to 2016 (17 years) there were 11 games played.
7. By using the `christmas_games` table, you'll notice that Christmas games mostly occur on regular NFL days (Saturday, Sunday, and Monday). The 2009 and 2020 seasons had their Christmas Day game on a Friday.
