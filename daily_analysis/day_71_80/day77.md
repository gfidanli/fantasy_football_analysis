# Day 77
Today I'm going to start a multi-day project where I take a look at under/over performers in the fantasy playoffs. To calculate performance I'll get the ranking of each player (by season) for the *fantasy* regular season and compare against their ranking for the *fantasy* playoffs, which is 3 weeks right before the end of the NFL regular season.  

Note: I have data from 1999-2022. For 1999-2021, the NFL regular season was 17 weeks which means fantasy regular season ocurred during weeks 1-13 and the playoffs were weeks 14-16. For 2022, since the NFL added another game to the schedule, regular season ocurred during weeks 1-14 and playoffs were weeks 15-17.

## Query
First thing I need to do is get regular season and playoff rankings for each player by season.

```sql
WITH reg_season_rankings_1999_2021 AS (
    SELECT
        season,
        player_name,
        position,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY tot_pts DESC) AS r_pts_reg_season,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY tot_pts_ppr DESC) AS r_pts_ppr_reg_season
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            SUM(fantasy_points) AS tot_pts,
            SUM(fantasy_points_ppr) AS tot_pts_ppr
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
        RANK() OVER(PARTITION BY season ORDER BY tot_pts DESC) AS r_pts_reg_season,
        RANK() OVER(PARTITION BY season ORDER BY tot_pts_ppr DESC) AS r_pts_ppr_reg_season
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            SUM(fantasy_points) AS tot_pts,
            SUM(fantasy_points_ppr) AS tot_pts_ppr
        FROM weekly
        WHERE season = 2022
            AND week < 15
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
        DENSE_RANK() OVER(PARTITION BY season ORDER BY tot_pts DESC) AS r_pts_playoffs,
        DENSE_RANK() OVER(PARTITION BY season ORDER BY tot_pts_ppr DESC) AS r_pts_ppr_playoffs
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            SUM(fantasy_points) AS tot_pts,
            SUM(fantasy_points_ppr) AS tot_pts_ppr
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
        RANK() OVER(PARTITION BY season ORDER BY tot_pts DESC) AS r_pts_playoffs,
        RANK() OVER(PARTITION BY season ORDER BY tot_pts_ppr DESC) AS r_pts_ppr_playoffs
    FROM
    (
        SELECT
            season,
            player_display_name AS player_name,
            position,
            SUM(fantasy_points) AS tot_pts,
            SUM(fantasy_points_ppr) AS tot_pts_ppr
        FROM weekly
        WHERE season = 2022
            AND week BETWEEN 15 AND 17
        GROUP BY season, player_display_name, position
        
    )
), fantasy_playoffs AS (
    SELECT *
    FROM playoff_rankings_1999_2021
    UNION ALL
    SELECT *
    FROM playoff_rankings_2022
)
-- PPR Only
SELECT
    reg.season,
    reg.player_name,
    reg.position,
    -- r_pts_reg_season,
    r_pts_ppr_reg_season,
    -- r_pts_playoffs,
    r_pts_ppr_playoffs,
    (r_pts_ppr_playoffs - r_pts_ppr_reg_season) AS r_diff
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
ORDER BY r_diff DESC
LIMIT 25
;
```

## Results – Top 25 Underperformers
| season | player_name         | position | r_pts_ppr_reg_season | r_pts_ppr_playoffs | r_diff |
| :----- | :------------------ | :------- | :------------------- | :----------------- | :----- |
| 2007   | Willis McGahee      | RB       | 17                   | 141                | 124    |
| 2000   | Eric Moulds         | WR       | 17                   | 140                | 123    |
| 2002   | Marshall Faulk      | RB       | 10                   | 133                | 123    |
| 2006   | Steve Smith         | WR       | 13                   | 136                | 123    |
| 2008   | T.J. Houshmandzadeh | WR       | 28                   | 149                | 121    |
| 1999   | Duce Staley         | RB       | 21                   | 138                | 117    |
| 2020   | Tyler Lockett       | WR       | 26                   | 143                | 117    |
| 2009   | Steven Jackson      | RB       | 15                   | 129                | 114    |
| 1999   | James Stewart       | RB       | 32                   | 144                | 112    |
| 2010   | Peyton Hillis       | RB       | 3                    | 114                | 111    |
| 2020   | James Robinson      | RB       | 17                   | 128                | 111    |
| 2001   | Troy Brown          | WR       | 10                   | 119                | 109    |
| 2003   | Domanick Williams   | RB       | 35                   | 143                | 108    |
| 2015   | Calvin Johnson      | WR       | 26                   | 134                | 108    |
| 2015   | Larry Fitzgerald    | WR       | 14                   | 120                | 106    |
| 1999   | Cris Carter         | WR       | 4                    | 109                | 105    |
| 2007   | Antonio Gates       | TE       | 23                   | 127                | 104    |
| 2007   | Joey Galloway       | WR       | 40                   | 144                | 104    |
| 2013   | Calvin Johnson      | WR       | 2                    | 106                | 104    |
| 2016   | Amari Cooper        | WR       | 32                   | 136                | 104    |
| 2000   | Michael Pittman     | RB       | 25                   | 128                | 103    |
| 2001   | Ricky Williams      | RB       | 8                    | 111                | 103    |
| 2006   | Chad Johnson        | WR       | 5                    | 108                | 103    |
| 2007   | Terrell Owens       | WR       | 5                    | 108                | 103    |
| 2011   | Mike Williams       | WR       | 37                   | 140                | 103    |

These are the top 25 *underachievers* by my metric, `r_diff` which is simply ranking through playoffs - ranking through regular season. For example, look at Peyton Hillis in 2010 – ranked 3rd in PPR through week 13 and then disappears in the fantasy playoffs (weeks 14-16). He might've costed you the playoffs!  

Or take Calvin Johnson in 2013. One of the best Wide Receivers to ever play the game (and #2 through the regular season) was the 106th-ranked player during the playoffs. It may have seemed nuts to bench him but if you did you likely would've done a lot better.

By changing the sort order of `r_diff` we can get the top 25 overachievers...

## Results – Top 25 Overperformers
| season | player_name       | position | r_pts_ppr_reg_season | r_pts_ppr_playoffs | r_diff |
| :----- | :---------------- | :------- | :------------------- | :----------------- | :----- |
| 2003   | Kevan Barlow      | RB       | 107                  | 5                  | -102   |
| 2007   | Brandon Jacobs    | RB       | 127                  | 27                 | -100   |
| 2014   | C.J. Anderson     | RB       | 111                  | 11                 | -100   |
| 2015   | David Johnson     | RB       | 103                  | 3                  | -100   |
| 2011   | DeAngelo Williams | RB       | 134                  | 36                 | -98    |
| 2007   | Fred Taylor       | RB       | 112                  | 15                 | -97    |
| 2009   | Ahmad Bradshaw    | RB       | 126                  | 29                 | -97    |
| 2018   | Chris Carson      | RB       | 110                  | 13                 | -97    |
| 2007   | Andre Johnson     | WR       | 104                  | 8                  | -96    |
| 2008   | Pierre Thomas     | RB       | 98                   | 4                  | -94    |
| 2020   | David Johnson     | RB       | 128                  | 36                 | -92    |
| 2004   | Lee Evans         | WR       | 99                   | 9                  | -90    |
| 2009   | Jamaal Charles    | RB       | 98                   | 8                  | -90    |
| 2017   | Dion Lewis        | RB       | 104                  | 14                 | -90    |
| 2021   | David Montgomery  | RB       | 113                  | 25                 | -88    |
| 2010   | LeGarrette Blount | RB       | 147                  | 61                 | -86    |
| 2020   | Miles Sanders     | RB       | 112                  | 29                 | -83    |
| 2004   | Kevin Jones       | RB       | 97                   | 15                 | -82    |
| 2001   | Dominic Rhodes    | RB       | 85                   | 4                  | -81    |
| 2001   | Stacey Mack       | RB       | 90                   | 9                  | -81    |
| 2017   | C.J. Anderson     | RB       | 100                  | 19                 | -81    |
| 1999   | Patrick Jeffers   | WR       | 82                   | 2                  | -80    |
| 2005   | Corey Dillon      | RB       | 84                   | 6                  | -78    |
| 2010   | Kenny Britt       | WR       | 118                  | 40                 | -78    |
| 2021   | George Kittle     | TE       | 90                   | 13                 | -77    |

David Johnson was a 2-time league winner! Pretty cool. Interestingly enough no player performances from 2022 show up. 

## Caveats
I added a couple filters to the query to narrow down the results:

1. No quarterbacks. I was getting too many instances of backup QBs coming in and overachieving. Makes sense but takes away from what I'm trying to look at here which are the players that you could have benched or added that turned out to be league winners or losers. In most cases you have a QB you stick with and don't stream. I may look into QBs in the future though.
2. I limited the playoff rankings to the top 150 players. I was getting cases of injured players becoming the underperformers. Like with the QBs, not having this filter would add noise to the dataset. I wanted to show that some really good players have really bad slumps and I wanted to highlight the players whose slumps ocurred during the worst possible time. 