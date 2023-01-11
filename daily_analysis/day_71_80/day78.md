# Day 78
Today I'll take the same basic query as yesterday and substitute `AVG()` for `SUM()` when calculating rankings for the regular season and playoff performances.

## Query
Note: I added an extra filter for the 2022 season to exclude players from Cincinnati and Buffalo due to the their week 17 game being postponed. Doesn't make sense to calculate their playoff average since it would be too low.

```sql
WITH reg_season_rankings_1999_2021 AS (
    SELECT
        season,
        player_name,
        position,
        avg_pts,
        avg_pts_ppr,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY avg_pts DESC) AS r_pts_reg_season,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY avg_pts_ppr DESC) AS r_pts_ppr_reg_season
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            ROUND(AVG(fantasy_points), 2) AS avg_pts,
            ROUND(AVG(fantasy_points_ppr), 2) AS avg_pts_ppr
        FROM weekly
        WHERE season < 2022
            AND week < 14
        GROUP BY season, player_display_name, position
        
    )
), reg_season_rankings_2022 AS (
    SELECT
        season,
        player_name,
        position,
        avg_pts,
        avg_pts_ppr,
        RANK() OVER(PARTITION BY season ORDER BY avg_pts DESC) AS r_pts_reg_season,
        RANK() OVER(PARTITION BY season ORDER BY avg_pts_ppr DESC) AS r_pts_ppr_reg_season
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            ROUND(AVG(fantasy_points), 2) AS avg_pts,
            ROUND(AVG(fantasy_points_ppr), 2) AS avg_pts_ppr
        FROM weekly
        WHERE season = 2022
            AND week < 15
            AND recent_team NOT IN ('CIN', 'BUF')
        GROUP BY season, player_display_name, position
        
    )
), fantasy_reg_season AS (
    SELECT *
    FROM reg_season_rankings_1999_2021
    UNION ALL
    SELECT *
    FROM reg_season_rankings_2022
), playoff_rankings_1999_2021 AS (
    SELECT
        season,
        player_name,
        position,
        avg_pts,
        avg_pts_ppr,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY avg_pts DESC) AS r_pts_playoffs,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY avg_pts_ppr DESC) AS r_pts_ppr_playoffs
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            ROUND(AVG(fantasy_points), 2) AS avg_pts,
            ROUND(AVG(fantasy_points_ppr), 2) AS avg_pts_ppr
        FROM weekly
        WHERE season < 2022
            AND week BETWEEN 14 AND 16
        GROUP BY season, player_display_name, position
        
    )
), playoff_rankings_2022 AS (
    SELECT
        season,
        player_name,
        position,
        avg_pts,
        avg_pts_ppr,
        RANK() OVER(PARTITION BY season ORDER BY avg_pts DESC) AS r_pts_playoffs,
        RANK() OVER(PARTITION BY season ORDER BY avg_pts_ppr DESC) AS r_pts_ppr_playoffs
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            ROUND(AVG(fantasy_points), 2) AS avg_pts,
            ROUND(AVG(fantasy_points_ppr), 2) AS avg_pts_ppr
        FROM weekly
        WHERE season = 2022
            AND week BETWEEN 15 AND 17
            AND recent_team NOT IN ('CIN', 'BUF')
        GROUP BY season, player_display_name, position
        
    )
), fantasy_playoffs AS (
    SELECT *
    FROM playoff_rankings_1999_2021
    UNION ALL
    SELECT *
    FROM playoff_rankings_2022
), player_season_ppr AS (
    SELECT
        reg.season,
        reg.player_name,
        reg.position,
        -- r_pts_reg_season,
        reg.avg_pts_ppr AS avg_reg_season,
        r_pts_ppr_reg_season,
        -- r_pts_playoffs,
        play.avg_pts_ppr AS avg_playoffs,
        r_pts_ppr_playoffs,
        -- (r_pts_ppr_playoffs - r_pts_ppr_reg_season) AS r_diff,
        ROUND(((play.avg_pts_ppr - reg.avg_pts_ppr)/reg.avg_pts_ppr) * 100, 2) AS pct_change
    FROM fantasy_reg_season AS reg
    INNER JOIN fantasy_playoffs AS play
        ON play.season = reg.season
        AND play.player_name = reg.player_name
        AND play.position = reg.position
    WHERE r_pts_reg_season <= 100
        -- QBs tend to add noise
        AND reg.position <> 'QB'
        -- Don't want to add injured players
        AND r_pts_ppr_playoffs < 150
    ORDER BY pct_change ASC
)
SELECT *
FROM player_season_ppr
LIMIT 20
;
```

## Results – Top 20 Underperformers
| season | player_name         | position | avg_reg_season | r_pts_ppr_reg_season | avg_playoffs | r_pts_ppr_playoffs | pct_change |
| :----- | :------------------ | :------- | :------------- | :------------------- | :----------- | :----------------- | :--------- |
| 2000   | Eric Moulds         | WR       | 19.95          | 15                   | 5.47         | 143                | -72.58     |
| 2004   | Terrell Owens       | WR       | 22.12          | 5                    | 6.5          | 146                | -70.61     |
| 2002   | Marshall Faulk      | RB       | 24.73          | 3                    | 7.47         | 134                | -69.79     |
| 2006   | Steve Smith         | WR       | 20.83          | 5                    | 7.27         | 133                | -65.1      |
| 2000   | Michael Pittman     | RB       | 16.79          | 33                   | 6.17         | 131                | -63.25     |
| 2007   | Terrell Owens       | WR       | 23.37          | 5                    | 8.87         | 123                | -62.05     |
| 2005   | LaDainian Tomlinson | RB       | 26.58          | 1                    | 10.23        | 95                 | -61.51     |
| 2008   | Anquan Boldin       | WR       | 24.09          | 1                    | 9.3          | 115                | -61.39     |
| 2006   | Chester Taylor      | RB       | 16.53          | 23                   | 6.75         | 145                | -59.17     |
| 2003   | David Boston        | WR       | 16.51          | 23                   | 6.8          | 130                | -58.81     |
| 2009   | DeAngelo Williams   | RB       | 17.24          | 20                   | 7.15         | 140                | -58.53     |
| 2013   | Andre Brown         | RB       | 17.95          | 24                   | 7.53         | 145                | -58.05     |
| 2013   | Calvin Johnson      | WR       | 24.72          | 2                    | 10.43        | 104                | -57.81     |
| 2016   | Larry Fitzgerald    | WR       | 17.21          | 32                   | 7.33         | 149                | -57.41     |
| 2010   | Peyton Hillis       | RB       | 21.94          | 3                    | 9.67         | 113                | -55.93     |
| 2001   | Ricky Williams      | RB       | 19.74          | 10                   | 8.73         | 108                | -55.78     |
| 2018   | Adam Thielen        | WR       | 22.55          | 7                    | 10.0         | 106                | -55.65     |
| 2000   | Stephen Davis       | RB       | 18.99          | 18                   | 8.47         | 102                | -55.4      |
| 2006   | Chad Johnson        | WR       | 19.25          | 8                    | 8.7          | 113                | -54.81     |
| 2018   | James White         | RB       | 19.4           | 30                   | 8.97         | 117                | -53.76     |

When looking at averages it's easier to interpret the results. The rankings change slightly – we now have a few top 5 players by average ppr through the fantasy regular season. The drop off is very bad for these players, going from 20+ points a game to single digits. The worst thing is, because they were studs you likely kept them in for multiple playoff weeks (if you were able to advance) and based on the low averages, it would have been better to swap them for a bench player who could give you 10+!

Like yesterday I can flip the sort order to get the playoff overperformers...

## Results – Top 20 Overperformers
| season | player_name        | position | avg_reg_season | r_pts_ppr_reg_season | avg_playoffs | r_pts_ppr_playoffs | pct_change |
| :----- | :----------------- | :------- | :------------- | :------------------- | :----------- | :----------------- | :--------- |
| 2000   | Warrick Dunn       | RB       | 11.45          | 84                   | 32.37        | 2                  | 182.71     |
| 2020   | Myles Gaskin       | RB       | 14.08          | 77                   | 33.9         | 1                  | 140.77     |
| 2004   | Drew Bennett       | WR       | 13.75          | 59                   | 32.97        | 1                  | 139.78     |
| 2008   | Pierre Thomas      | RB       | 10.65          | 99                   | 24.93        | 3                  | 134.08     |
| 2021   | Damien Harris      | RB       | 12.23          | 99                   | 28.3         | 5                  | 131.4      |
| 2006   | Maurice Jones-Drew | RB       | 13.81          | 46                   | 31.93        | 2                  | 131.21     |
| 2020   | David Johnson      | RB       | 11.7           | 107                  | 26.6         | 6                  | 127.35     |
| 2008   | Antonio Bryant     | WR       | 13.71          | 52                   | 29.5         | 1                  | 115.17     |
| 2009   | Jamaal Charles     | RB       | 11.18          | 97                   | 23.83        | 7                  | 113.15     |
| 2017   | Dion Lewis         | RB       | 9.39           | 131                  | 19.67        | 19                 | 109.48     |
| 1999   | Corey Dillon       | RB       | 11.86          | 73                   | 24.5         | 8                  | 106.58     |
| 2003   | Clinton Portis     | RB       | 20.69          | 8                    | 42.45        | 1                  | 105.17     |
| 2001   | Stacey Mack        | RB       | 9.86           | 109                  | 20.1         | 13                 | 103.85     |
| 2021   | Mark Andrews       | TE       | 14.92          | 63                   | 30.2         | 2                  | 102.41     |
| 1999   | Marcus Robinson    | WR       | 15.32          | 26                   | 30.65        | 4                  | 100.07     |
| 2000   | James Allen        | RB       | 9.94           | 112                  | 19.6         | 20                 | 97.18      |
| 2014   | Odell Beckham      | WR       | 18.81          | 18                   | 36.67        | 1                  | 94.95      |
| 2013   | Ryan Mathews       | RB       | 10.81          | 122                  | 21.07        | 16                 | 94.91      |
| 2004   | Larry Johnson      | RB       | 14.05          | 56                   | 27.2         | 4                  | 93.59      |
| 2005   | Larry Johnson      | RB       | 17.98          | 18                   | 34.8         | 1                  | 93.55      |

It's interesting, the players on this list aren't necessarily bad players. Their rankings show that they're between elite start-every-week players and average. But in the playoffs, they went absolutely nuts, oftentimes doubling their average through the regular season.  

Take Mark Andrews for example. He's a start-every-week Tight End but it's a position notorious for being shallow. They just don't score a lot of points. Andrews ended up averaging 30 points throughout the fantasy playoffs! Easily a league-winner due to being able to outscore your opponent at the TE position by a wide margin.

## Caveats
I added a couple filters to the query to narrow down the results:

1. No quarterbacks. I was getting too many instances of backup QBs coming in and overachieving. Makes sense but takes away from what I'm trying to look at here which are the players that you could have benched or added that turned out to be league winners or losers. In most cases you have a QB you stick with and don't stream. I may look into QBs in the future though.
2. I limited the playoff rankings to the top 150 players. I was getting cases of injured players becoming the underperformers. Like with the QBs, not having this filter would add noise to the dataset. I wanted to show that some really good players have really bad slumps and I wanted to highlight the players whose slumps ocurred during the worst possible time. 