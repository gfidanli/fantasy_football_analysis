# Day 59
Given that it's Thursday Night Football today between the Jacksonville Jaguars and the New York Jets, I thought I'd combine a couple of tables that I've been working on recently to see not only the offensive snaps percentage of these players but also their TD efficiency in the end zone.  

I'm going to limit the analysis to just the last 3 weeks of data (Weeks 12-15) to make sure that I'm looking at recent trends.

## Offensive Snap Percentage
Offensive snap percentage is pretty simple, what is the percentage of offensive plays that the player was on the field for? A value of 100 means that every time the offense took the field, that player had an opportunity to get the ball and thus score fantasy points.

### Query

First I'll process the Red Zone TD Efficiency table and save it as a `view`:

#### Red Zone TD Efficiency View
```sql
CREATE view td_efficiency AS
WITH data_table AS
(
	SELECT  *
	       ,COUNT(*)                                  AS num_plays
	       ,COUNT(CASE WHEN touchdown = 1 THEN 1 END) AS count_td
	FROM
	(
		SELECT  week
		       ,posteam AS team
		       ,play_type
		       ,CASE WHEN play_type = 'run' THEN rusher_player_id  ELSE receiver_player_id END AS player_id
		       ,touchdown
		FROM pbp
		WHERE season = 2022
		AND week <= 15
		AND yardline_100 <= 20
		AND play_type IN ('run', 'pass')
		AND two_point_attempt = 0
	)
	GROUP BY  team
	         ,play_type
	         ,player_id
	         ,week
)
SELECT  week
       ,team
       ,play_type
       ,player_name
       ,num_plays
       ,count_td
FROM data_table
LEFT JOIN
(
	-- This will ensure that there are no duplicate rows
	SELECT DISTINCT player_id
	       ,player_display_name AS player_name
	FROM weekly
) AS weekly_temp
ON weekly_temp.player_id = data_table.player_id
-- only bring in plays that were successful (did not have to score a TD)
WHERE player_name IS NOT NULL
```

Now I `JOIN` the two tables together, utilizing a `CTE` to pre-process the offensive snaps table before the join...

#### Main Query

```sql
WITH offense_snaps AS (
    SELECT  recent_team                     AS team
       ,weekly.position
       ,player_display_name             AS player_name
       ,ROUND(AVG(offense_pct) * 100, 2) AS avg_off_snap_pct
    FROM weekly
    LEFT JOIN snap_counts
        ON snap_counts.player = weekly.player_display_name
            /*
            Normally, I would use a player_id field to join the tables.
            However, there isn't an id in either table or an intermediate
            table that can bring in all the players. So I needed to be 
            creative and use multiple fields to make sure I got the correct
            player as there can be multiple players with the same name
            */
            AND snap_counts.team = weekly.recent_team
            AND snap_counts.position = weekly.position
            AND snap_counts.season = weekly.season
            AND snap_counts.week = weekly.week
    WHERE weekly.season = 2022
        AND weekly.week BETWEEN 13 AND 15
        AND recent_team IN ('JAX', 'NYJ') -- Only focus on today's TNF game
        AND weekly.position IN ('QB', 'RB', 'WR', 'TE')
    GROUP BY player_name
    ORDER BY team, weekly.position, 4 DESC
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
        FROM td_efficiency
        WHERE team IN ('JAX', 'NYJ')
        AND week BETWEEN 13 AND 15
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

### Result – Jacksonville Players Red Zone TD Efficiency and Offensive Snap Percentage Weeks 13-15
| team | position | play_type | player_name     | avg_off_snap_pct | tot_rz_plays | tot_rz_tds | rz_td_pct |
| :--- | :------- | :-------- | :-------------- | :--------------- | :----------- | :--------- | :-------- |
| JAX  | RB       | run       | Travis Etienne  | 78.67            | 10           | 0          | 0.0       |
| JAX  | WR       | pass      | Zay Jones       | 85.33            | 6            | 3          | 50.0      |
| JAX  | TE       | pass      | Evan Engram     | 80.67            | 5            | 2          | 40.0      |
| JAX  | WR       | pass      | Christian Kirk  | 86.67            | 4            | 0          | 0.0       |

Zay Jones has been hot the past 3 weeks and Travis Etienne could be due for some positive TD regression. 

### Result – Jets Players Red Zone TD Efficiency and Offensive Snap Percentage Weeks 13-15
| team | position | play_type | player_name     | avg_off_snap_pct | tot_rz_plays | tot_rz_tds | rz_td_pct |
| :--- | :------- | :-------- | :-------------- | :--------------- | :----------- | :--------- | :-------- |
| NYJ  | RB       | run       | Zonovan Knight  | 50.0             | 6            | 1          | 16.67     |
| NYJ  | WR       | pass      | Garrett Wilson  | 95.67            | 5            | 0          | 0.0       |
| NYJ  | WR       | pass      | Elijah Moore    | 75.0             | 4            | 0          | 0.0       |
| NYJ  | WR       | pass      | Corey Davis     | 46.5             | 4            | 0          | 0.0       |
| NYJ  | QB       | run       | Mike White      | 95.5             | 3            | 1          | 33.33     |
| NYJ  | WR       | pass      | Braxton Berrios | 30.0             | 3            | 0          | 0.0       |
| NYJ  | RB       | pass      | Zonovan Knight  | 50.0             | 2            | 0          | 0.0       |

Zonovan Knight has seen a lot of Red Zone usage in both the rushing and passing game. Garett Wilson is leading in offensive snaps for the skill position players. Combine that with high Red Zone attempts without a TD and he could have a big night.