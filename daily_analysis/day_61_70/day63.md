# Day 63
**Note**: The original post was mislabeled and was supposed to be `day62.md`. I've copied the original upload to `day62.md` and have changed this post to a new analysis.  

Today I'm going to re-use much of what I did for `day59.md` to analyze today's Monday Night Football game between the LA Chargers and the Indianapolis Colts. It'll be a little different since I can now use the `red_zone_efficiency` table I added to `etl.py` instead of creating a new view.

I'm going to limit the analysis to just the last 4 weeks of data (Weeks 12-15) to make sure that I'm looking at recent trends.

## Offensive Snap Percentage
Offensive snap percentage is pretty simple, what is the percentage of offensive plays that the player was on the field for? A value of 100 means that every time the offense took the field, that player had an opportunity to get the ball and thus score fantasy points.

### Query

```sql
WITH offense_snaps AS (
    SELECT  
        team
       ,position
       ,player             AS player_name
       ,ROUND(AVG(offense_pct) * 100, 2) AS avg_off_snap_pct
    FROM snap_counts
    WHERE season = 2022
        AND week BETWEEN 12 AND 15
        AND team IN ('LAC', 'IND') -- Only focus on today's game
        AND position IN ('QB', 'RB', 'WR', 'TE')
    GROUP BY player_name
    ORDER BY team, position, 4 DESC
)
SELECT  offense_snaps.team
       ,offense_snaps.position
       ,play_type
       ,offense_snaps.player_name
       ,avg_off_snap_pct
       ,tot_plays AS tot_rz_plays
       ,tot_tds   AS tot_rz_tds
       ,td_pct    AS rz_td_pct
FROM 
(
   SELECT  *
       ,ROUND((1.0 * tot_tds / tot_plays) * 100,2) AS td_pct
    FROM
    (
        SELECT  team
            ,play_type
            ,player_name
            ,SUM(num_plays) AS tot_plays
            ,SUM(count_td)  AS tot_tds
        FROM red_zone_efficiency
        WHERE team IN ('LAC', 'IND')
        AND week BETWEEN 12 AND 15
        GROUP BY  team
                ,play_type
                ,player_name
        HAVING tot_plays > 1
    )
) AS tds
    LEFT JOIN offense_snaps
        ON offense_snaps.player_name = tds.player_name
            AND offense_snaps.team = tds.team
ORDER BY 
    tds.team, 
    tot_rz_plays DESC, 
    avg_off_snap_pct DESC
;
```

### Result – Indianapolis Players Red Zone TD Efficiency and Offensive Snap Percentage Weeks 12-15
| team | position | play_type | player_name     | avg_off_snap_pct | tot_rz_plays | tot_rz_tds | rz_td_pct |
| :--- | :------- | :-------- | :-------------- | :--------------- | :----------- | :--------- | :-------- |
| IND  | RB       | run       | Jonathan Taylor | 59.0             | 9            | 1          | 11.11     |
| IND  | RB       | run       | Zack Moss       | 25.33            | 8            | 0          | 0.0       |
| IND  | RB       | run       | Deon Jackson    | 16.33            | 3            | 0          | 0.0       |
| IND  | QB       | run       | Matt Ryan       | 100.0            | 2            | 0          | 0.0       |
| IND  | WR       | pass      | Ashton Dulin    | 28.33            | 2            | 1          | 50.0      |

We know that Jonathan Taylor is out so it'll be the Zack Moss show. Good thing is that he's due for some positive TD regression.

### Result – LA Chargers Players Red Zone TD Efficiency and Offensive Snap Percentage Weeks 12-15
| team | position | play_type | player_name     | avg_off_snap_pct | tot_rz_plays | tot_rz_tds | rz_td_pct |
| :--- | :------- | :-------- | :-------------- | :--------------- | :----------- | :--------- | :-------- |
| LAC  | RB       | run       | Austin Ekeler   | 64.5             | 11           | 2          | 18.18     |
| LAC  | WR       | pass      | Keenan Allen    | 90.0             | 9            | 1          | 11.11     |
| LAC  | RB       | pass      | Austin Ekeler   | 64.5             | 8            | 1          | 12.5      |
| LAC  | TE       | pass      | Gerald Everett  | 62.75            | 5            | 0          | 0.0       |
| LAC  | RB       | run       | Joshua Kelley   | 34.75            | 5            | 1          | 20.0      |
| LAC  | QB       | run       | Justin Herbert  | 100.0            | 4            | 0          | 0.0       |

Ekeler gets the vast majority of touches in the Red Zone an is due for some positive TD regression. Check Keenan Allen's snap share – 90%! I'd expect him to find the end zone. Finally, expect Herbert to eventually find the end zone with his legs. The chargers aren't afraid to run him near the goal line. Even Gerald Everett could be due given his snap share.  

## Yards and Touchdowns Allowed to Opponents
I'll go a step further and take a look at how each team ranks on average passing yards, average passing touchdowns, and average rushing touchdowns they've *allowed to opponents* over the last 4 weeks (Weeks 12 to 15).

### Query
```sql
WITH totals_by_team AS (
        -- Get the totals per week
        SELECT  recent_team
                ,week
                ,SUM(passing_yards) AS tot_pass_yds
                ,SUM(passing_tds)   AS tot_pass_tds
                ,SUM(rushing_tds)   AS tot_rush_tds
        FROM weekly
        WHERE season = 2022
            AND week <= 15
            -- will only consider stats from offensive skill players
            AND position in ('QB', 'RB', 'WR', 'TE') 
        GROUP BY recent_team, week),
    -- Get schedule info
        home_games AS (
            SELECT  game_id
                    ,season
                    ,week
                    ,home_team AS team
                    ,away_team AS opp_team
            FROM schedules
            WHERE season = 2022
                AND week <= 15
        ),
        away_games AS (
            SELECT  game_id
                ,season
                ,week
                ,away_team AS team
                ,home_team AS opp_team
            FROM schedules
            WHERE season = 2022
                AND week <= 15
        ),
        stacked AS (
            SELECT *
            FROM home_games
            UNION
            SELECT *
            FROM away_games
        ),
    -- Join the two temp datasets
    -- Every team will have it's total fantasy points per team appended to it
    joined_data AS (
        SELECT  game_id
                ,season
                ,stacked.week
                ,team
                ,opp_team
                ,tot_pass_yds
                ,tot_pass_tds
                ,tot_rush_tds
        FROM stacked
        LEFT JOIN totals_by_team
            ON totals_by_team.recent_team = stacked.team
            AND totals_by_team.week = stacked.week),
    -- Only use opp_team to get the points scored scored against
    avg_scored_against AS (
        SELECT  opp_team
                ,ROUND(AVG(tot_pass_yds),2) AS avg_pass_yds
                ,ROUND(AVG(tot_pass_tds),2) AS avg_pass_tds
                ,ROUND(AVG(tot_rush_tds),2) AS avg_rush_tds
        FROM joined_data
        WHERE week BETWEEN 12 and 15
        GROUP BY opp_team),
    rankings AS (
        SELECT  opp_team                                       AS team
                ,avg_pass_yds
                ,DENSE_RANK() OVER(ORDER BY avg_pass_yds DESC) AS r_pass_yds
                ,avg_pass_tds
                ,DENSE_RANK() OVER(ORDER BY avg_pass_tds DESC) AS r_pass_tds
                ,avg_rush_tds
                ,DENSE_RANK() OVER(ORDER BY avg_rush_tds DESC) AS r_rush_tds
        FROM avg_scored_against
        ORDER BY r_pass_tds)
SELECT *
FROM rankings
;
```

### Result – By Avg Passing Touchdowns Allowed per Game
| team | avg_pass_yds | r_pass_yds | avg_pass_tds | r_pass_tds | avg_rush_tds | r_rush_tds |
| :--- | :----------- | :--------- | :----------- | :--------- | :----------- | :--------- |
| IND  | 268.0        | 8          | 2.33         | 1          | 2.0          | 1          |
| KC   | 194.5        | 25         | 2.25         | 2          | 0.5          | 10         |
| MIA  | 288.0        | 4          | 2.0          | 3          | 0.5          | 10         |
| JAX  | 276.0        | 5          | 2.0          | 3          | 1.25         | 6          |
| NE   | 254.75       | 11         | 2.0          | 3          | 0.5          | 10         |
| DAL  | 248.0        | 14         | 2.0          | 3          | 0.5          | 10         |
| TB   | 213.75       | 20         | 2.0          | 3          | 1.25         | 6          |
| PHI  | 194.5        | 25         | 2.0          | 3          | 0.75         | 8          |
| ATL  | 188.67       | 27         | 2.0          | 3          | 0.0          | 12         |
| TEN  | 335.5        | 1          | 1.75         | 4          | 1.5          | 4          |
| DET  | 295.0        | 3          | 1.75         | 4          | 0.5          | 10         |
| NYG  | 250.5        | 13         | 1.75         | 4          | 1.5          | 4          |
| MIN  | 315.75       | 2          | 1.5          | 5          | 0.5          | 10         |
| CIN  | 275.5        | 6          | 1.5          | 5          | 0.5          | 10         |
| SEA  | 202.5        | 22         | 1.5          | 5          | 1.75         | 2          |
| CHI  | 270.67       | 7          | 1.33         | 6          | 2.0          | 1          |
| ARI  | 235.33       | 17         | 1.33         | 6          | 1.33         | 5          |
| CAR  | 195.0        | 24         | 1.33         | 6          | 1.0          | 7          |
| LA   | 263.25       | 10         | 1.25         | 7          | 1.0          | 7          |
| BAL  | 236.75       | 16         | 1.25         | 7          | 0.25         | 11         |
| BUF  | 234.5        | 18         | 1.25         | 7          | 0.75         | 8          |
| CLE  | 206.0        | 21         | 1.25         | 7          | 0.25         | 11         |
| LAC  | 192.75       | 26         | 1.25         | 7          | 1.0          | 7          |
| HOU  | 264.0        | 9          | 1.0          | 8          | 1.25         | 6          |
| LV   | 251.25       | 12         | 1.0          | 8          | 1.0          | 7          |
| SF   | 247.5        | 15         | 1.0          | 8          | 0.0          | 12         |
| DEN  | 221.75       | 19         | 1.0          | 8          | 0.75         | 8          |
| NO   | 200.0        | 23         | 1.0          | 8          | 0.67         | 9          |
| NYJ  | 187.75       | 28         | 1.0          | 8          | 0.75         | 8          |
| GB   | 172.67       | 31         | 1.0          | 8          | 1.67         | 3          |
| PIT  | 173.75       | 30         | 0.75         | 9          | 0.5          | 10         |
| WAS  | 178.0        | 29         | 0.67         | 10         | 0.67         | 9          |

### Result – LA Chargers and Indianapolis Colts
| team | avg_pass_yds | r_pass_yds | avg_pass_tds | r_pass_tds | avg_rush_tds | r_rush_tds |
| :--- | :----------- | :--------- | :----------- | :--------- | :----------- | :--------- |
| IND  | 268.0        | 8          | 2.33         | 1          | 2.0          | 1          |
| LAC  | 192.75       | 26         | 1.25         | 7          | 1.0          | 7          |

Now we have to understand that the results are somewhat skewed by Indiana's last game in which they allowed Minnesota to come back from a huge deficit **and** the game went to OT. But still, they are number 1 in passing TDs and rushing TDs. Given that the Chargers as a whole are due for positive TD regression...it could be a good night for managers starting Chargers players.