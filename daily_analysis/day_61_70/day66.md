# Day 66
It's another Thursday Night Football game so I'll be providing the usual analysis in the form of offensive snap percentage and Red Zone efficiency. This post will be in a similar format to `day63.md` where I added an additional table, looking at average TDs allowed (by type) and average passing yards allowed by team and their respective rankings.  

Since I like to add something new each time I do one of these kinds of analysis, I'll add both rush share and target share to the player summary table. This should help to come to a better conclusion of who is more likely to get the ball in scoring situations (and who is more likely to score overall). More opportunities = more fantasy points. 

**Note**: Rush share and target share is calculated on a full game basis, not just Red Zone plays.

I'll to limit the analysis to the last 4 weeks of data (Weeks 13-16) to make sure that I'm looking at recent trends.

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
        AND week BETWEEN 13 AND 16
        AND team IN ('DAL', 'TEN') -- Only focus on today's game
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
        WHERE team IN ('DAL', 'TEN')
        AND week BETWEEN 13 AND 16
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

### Result – Dallas Cowboys Players Red Zone TD Efficiency and Offensive Snap Percentage Weeks 13-16
| team | position | play_type | player_name           | avg_off_snap_pct | avg_rush_share | avg_target_share | tot_rz_plays | tot_rz_tds | rz_td_pct |
| :--- | :------- | :-------- | :-------------------- | :--------------- | :------------- | :--------------- | :----------- | :--------- | :-------- |
| DAL  | RB       | run       | Ezekiel Elliott       | 50.75            | 47.26          | 8.09             | 15           | 3          | 20.0      |
| DAL  | RB       | run       | Tony Pollard          | 51.75            | 35.73          | 15.59            | 7            | 2          | 28.57     |
| DAL  | WR       | pass      | Michael Gallup        | 79.25            | 0.0            | 16.35            | 6            | 2          | 33.33     |
| DAL  | WR       | pass      | Noah Brown            | 74.75            | 0.0            | 14.44            | 4            | 2          | 50.0      |
| DAL  | WR       | pass      | CeeDee Lamb           | 86.5             | 2.08           | 23.37            | 3            | 1          | 33.33     |
| DAL  | TE       | pass      | Dalton Schultz        | 87.0             | 0.0            | 17.6             | 2            | 0          | 0.0       |
| DAL  | RB       | pass      | Tony Pollard          | 51.75            | 35.73          | 15.59            | 2            | 1          | 50.0      |

The Cowboys love to feed Zeke in the Red Zone but he's not that efficient. Tony Pollard is out tonight so expect Zeke to get almost all touches in or out of the Red Zone. If he doesn't end up with a rushing TD I'd be surprised.  

Regarding the passing game, Dalton Schultz could get a TD. He plays a majority of snaps with a good target share overall. Higher than two of the other Cowboys' receivers.

### Result – Tennessee Titans Players Red Zone TD Efficiency and Offensive Snap Percentage Weeks 13-16
| team | position | play_type | player_name           | avg_off_snap_pct | avg_rush_share | avg_target_share | tot_rz_plays | tot_rz_tds | rz_td_pct |
| :--- | :------- | :-------- | :-------------------- | :--------------- | :------------- | :--------------- | :----------- | :--------- | :-------- |
| TEN  | RB       | run       | Derrick Henry         | 68.75            | 72.34          | 12.64            | 8            | 2          | 25.0      |
| TEN  | WR       | pass      | Nick Westbrook-Ikhine | 87.0             | 0.0            | 12.94            | 4            | 1          | 25.0      |
| TEN  | RB       | pass      | Derrick Henry         | 68.75            | 72.34          | 12.64            | 3            | 0          | 0.0       |
| TEN  | WR       | pass      | Robert Woods          | 89.0             | 0.0            | 18.45            | 2            | 0          | 0.0       |
| TEN  | QB       | run       | Ryan Tannehill        | 88.67            | 11.8           | 0                | 2            | 1          | 50.0      |
| TEN  | TE       | pass      | Chigoziem Okonkwo     | 53.25            | 2.18           | 16.26            | 2            | 1          | 50.0      |

Derrick Henry dominates in the number of Red Zone touches as he should given that he's the Titan's best player.

## Yards and Touchdowns Allowed to Opponents
I'll go a step further and take a look at how each team ranks on average passing yards, average passing touchdowns, and average rushing touchdowns they've *allowed to opponents* over the last 4 weeks (Weeks 13 to 16).

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
            AND week <= 16
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
                AND week <= 16
        ),
        away_games AS (
            SELECT  game_id
                ,season
                ,week
                ,away_team AS team
                ,home_team AS opp_team
            FROM schedules
            WHERE season = 2022
                AND week <= 16
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
        WHERE week BETWEEN 13 and 16
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
WHERE team IN ('DAL', 'TEN')
;
```

### Result – By Avg Passing Yards and Touchdowns Allowed per Game
| team | avg_pass_yds | r_pass_yds | avg_pass_tds | r_pass_tds | avg_rush_tds | r_rush_tds |
| :--- | :----------- | :--------- | :----------- | :--------- | :----------- | :--------- |
| IND  | 288.33       | 5          | 2.33         | 1          | 2.0          | 2          |
| DAL  | 279.75       | 6          | 2.25         | 2          | 0.5          | 8          |
| KC   | 223.25       | 18         | 2.25         | 2          | 0.5          | 8          |
| MIA  | 293.75       | 4          | 2.0          | 3          | 0.5          | 8          |
| NE   | 271.0        | 7          | 2.0          | 3          | 0.5          | 8          |
| CAR  | 266.0        | 9          | 2.0          | 3          | 1.0          | 6          |
| NYG  | 260.0        | 11         | 2.0          | 3          | 1.0          | 6          |
| PHI  | 218.0        | 20         | 2.0          | 3          | 0.75         | 7          |
| TEN  | 322.5        | 1          | 1.75         | 4          | 1.25         | 5          |
| SF   | 268.75       | 8          | 1.75         | 4          | 0.0          | 10         |
| CIN  | 262.75       | 10         | 1.75         | 4          | 0.5          | 8          |
| JAX  | 258.0        | 12         | 1.75         | 4          | 1.0          | 6          |
| TB   | 215.5        | 21         | 1.75         | 4          | 1.0          | 6          |
| ATL  | 181.0        | 28         | 1.67         | 5          | 0.0          | 10         |
| DET  | 294.25       | 3          | 1.5          | 6          | 1.0          | 6          |
| MIN  | 303.75       | 2          | 1.25         | 7          | 0.75         | 7          |
| LA   | 248.0        | 13         | 1.25         | 7          | 0.75         | 7          |
| DEN  | 238.25       | 14         | 1.25         | 7          | 1.25         | 5          |
| SEA  | 184.75       | 27         | 1.25         | 7          | 1.5          | 3          |
| CHI  | 223.0        | 19         | 1.0          | 8          | 2.67         | 1          |
| BUF  | 210.5        | 24         | 1.0          | 8          | 0.5          | 8          |
| WAS  | 198.0        | 26         | 1.0          | 8          | 1.33         | 4          |
| LV   | 230.25       | 16         | 0.75         | 9          | 0.5          | 8          |
| HOU  | 212.5        | 22         | 0.75         | 9          | 1.5          | 3          |
| NYJ  | 200.25       | 25         | 0.75         | 9          | 1.0          | 6          |
| LAC  | 180.75       | 29         | 0.75         | 9          | 0.75         | 7          |
| CLE  | 167.5        | 31         | 0.75         | 9          | 0.75         | 7          |
| PIT  | 167.5        | 31         | 0.75         | 9          | 0.25         | 9          |
| ARI  | 237.67       | 15         | 0.67         | 10         | 1.33         | 4          |
| GB   | 225.0        | 17         | 0.67         | 10         | 1.0          | 6          |
| NO   | 171.0        | 30         | 0.67         | 10         | 1.0          | 6          |
| BAL  | 211.0        | 23         | 0.5          | 11         | 0.25         | 9          |

### Result – Dallas Cowboys and Tennessee Titans
| team | avg_pass_yds | r_pass_yds | avg_pass_tds | r_pass_tds | avg_rush_tds | r_rush_tds |
| :--- | :----------- | :--------- | :----------- | :--------- | :----------- | :--------- |
| DAL  | 279.75       | 6          | 2.25         | 2          | 0.5          | 8          |
| TEN  | 322.5        | 1          | 1.75         | 4          | 1.25         | 5          |

Dallas' defense hasn't been as dominant as it was the beginning of the season – they rank around the middle in terms of rushing and passing. Tennessee is a juicy matchup though. They rank first in average passing yards allowed and towards the upper third in passing and rushing touchdowns. I expect Cowboy studs CeeDee Lamb and Ezekiel Elliott do to well tonight.