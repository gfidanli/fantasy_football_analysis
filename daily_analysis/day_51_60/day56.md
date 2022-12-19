# Day 56
Today I wanted to look into Red Zone (plays within 20 yards of the opposing team's End Zone) efficiency for players where efficiency is defined as the number of touchdowns scored / the number of red zone plays run.  

To do this I brought in a few more fields from the play-by-play dataset: `yardline_100` and `play_type`. I filtered for all plays where `yardline_100 <= 20` AND `play_type IN ('pass', 'run')`. This gives me the pass and run plays where yards to the goal line are 20 or less.  

After this it was just a matter of grouping by `team`, `play_time`, and `player_name`. After that I can count the number of plays that featured that player, the number of those plays that resulted in a touchdown, and use those to calculate the ratio of touchdowns/total plays or red zone touchdown efficiency of the player.

## Query
```sql
WITH data_table AS
(
	SELECT
        *,
        CASE 
            WHEN play_type = 'run' THEN rusher_player_id
            ELSE receiver_player_id 
        END AS player_id
    FROM pbp
    WHERE season = 2022
        AND yardline_100 <= 20
        AND play_type IN ('run', 'pass') 
)
SELECT  *
       ,ROUND((1.0 * count_td / num_plays)*100,2) AS td_pct
FROM
(SELECT posteam                                    AS team
	    ,play_type
        ,player_name
	    ,COUNT(*)                                  AS num_plays
	    ,COUNT(CASE WHEN touchdown = 1 THEN 1 END) AS count_td
FROM data_table
LEFT JOIN
(
	-- This will ensure that there are no duplicate rows
    SELECT DISTINCT player_id, player_display_name AS player_name
	FROM weekly
) AS weekly_temp
    ON weekly_temp.player_id = data_table.player_id
GROUP BY team, play_type, player_name)
ORDER BY num_plays DESC, td_pct DESC
LIMIT 10
;
```

## Top 10 By Red Zone Volume
| team | play_type | player_name     | num_plays | count_td | td_pct |
| :--- | :-------- | :-------------- | :-------- | :------- | :----- |
| DET  | run       | Jamaal Williams | 47        | 13       | 27.66  |
| PHI  | run       | Jalen Hurts     | 43        | 11       | 25.58  |
| TEN  | run       | Derrick Henry   | 39        | 11       | 28.21  |
| PHI  | run       | Miles Sanders   | 39        | 10       | 25.64  |
| CLE  | run       | Nick Chubb      | 39        | 9        | 23.08  |
| JAX  | run       | Travis Etienne  | 38        | 4        | 10.53  |
| CIN  | run       | Joe Mixon       | 37        | 6        | 16.22  |
| MIN  | run       | Dalvin Cook     | 37        | 6        | 16.22  |
| LV   | run       | Josh Jacobs     | 36        | 9        | 25.0   |
| NYG  | run       | Saquon Barkley  | 36        | 8        | 22.22  |

Here's the top 10 by volume (ordering by `num_plays` first and then `td_pct`). Some thoughts..
- Jalen Hurts (a QB!) is a monster in the Red Zone. Not only does he run it in 25% of the time but he's also a threat to score with his arm.
- Jamaal Williams is able to convert at a high % even with a lot of volume. Detroit feeds him in the Red Zone because it works and opposing defenses can't see m to stop him.
- Travis Etienne gets a lot of attempts but his efficiency ranks quite low among the other backs wth high volume. Don't depend on him for a TD in these situations.

It's Monday Night Football tonight so I thought I'd look at the top 10 players by Red ZOne volume per team. It could help fantasy managers with their lineups.

## Top 10 By Red Zone Volume (Green Bay Packers)
### Query
```sql
WITH data_table AS
(
	SELECT
        *,
        CASE 
            WHEN play_type = 'run' THEN rusher_player_id
            ELSE receiver_player_id 
        END AS player_id
    FROM pbp
    WHERE season = 2022
        AND yardline_100 <= 20
        AND play_type IN ('run', 'pass') 
)
SELECT  *
       ,ROUND((1.0 * count_td / num_plays)*100,2) AS td_pct
FROM
(SELECT  posteam                                   AS team
	       ,play_type
           ,player_name
	       ,COUNT(*)                                  AS num_plays
	       ,COUNT(CASE WHEN touchdown = 1 THEN 1 END) AS count_td
FROM data_table
LEFT JOIN
(
	-- This will ensure that there are no duplicate rows
    SELECT DISTINCT player_id, player_display_name AS player_name
	FROM weekly
) AS weekly_temp
    ON weekly_temp.player_id = data_table.player_id
WHERE team = 'GB'
GROUP BY team, play_type, player_name)
ORDER BY team, num_plays DESC, td_pct DESC
LIMIT 10
;
```

### Result
| team | play_type | player_name      | num_plays | count_td | td_pct |
| :--- | :-------- | :--------------- | :-------- | :------- | :----- |
| GB   | run       | Aaron Jones      | 23        | 2        | 8.7    |
| GB   | pass      | Allen Lazard     | 13        | 4        | 30.77  |
| GB   | run       | A.J. Dillon      | 13        | 2        | 15.38  |
| GB   | pass      | Christian Watson | 8         | 4        | 50.0   |
| GB   | pass      | Robert Tonyan    | 8         | 1        | 12.5   |
| GB   | pass      | Aaron Jones      | 7         | 2        | 28.57  |
| GB   | pass      | Romeo Doubs      | 6         | 3        | 50.0   |
| GB   | pass      | Randall Cobb     | 6         | 1        | 16.67  |
| GB   | pass      | Sammy Watkins    | 5         | 0        | 0.0    |
| GB   | run       | Christian Watson | 3         | 1        | 33.33  |

Wow! Aaron Jones has been incredibly inefficient in the Red Zone this year. A.J. Dillon too. The Packers can't seem to convert on Red Zone rushing plays this year.  

Christian Watson is definitely a favorite Red Zone target...he's a WR that's also involved in rushing plays!

## Top 10 By Red Zone Volume (LA Rams)
### Query
```sql
WITH data_table AS
(
	SELECT
        *,
        CASE 
            WHEN play_type = 'run' THEN rusher_player_id
            ELSE receiver_player_id 
        END AS player_id
    FROM pbp
    WHERE season = 2022
        AND yardline_100 <= 20
        AND play_type IN ('run', 'pass') 
)
SELECT  *
       ,ROUND((1.0 * count_td / num_plays)*100,2) AS td_pct
FROM
(SELECT  posteam                                   AS team
	       ,play_type
           ,player_name
	       ,COUNT(*)                                  AS num_plays
	       ,COUNT(CASE WHEN touchdown = 1 THEN 1 END) AS count_td
FROM data_table
LEFT JOIN
(
	-- This will ensure that there are no duplicate rows
    SELECT DISTINCT player_id, player_display_name AS player_name
	FROM weekly
) AS weekly_temp
    ON weekly_temp.player_id = data_table.player_id
WHERE team = 'LA'
    AND player_name IS NOT NULL
GROUP BY team, play_type, player_name)
ORDER BY team, num_plays DESC, td_pct DESC
LIMIT 10
;
```

### Result
| team | play_type | player_name       | num_plays | count_td | td_pct |
| :--- | :-------- | :---------------- | :-------- | :------- | :----- |
| LA   | run       | Cam Akers         | 15        | 4        | 26.67  |
| LA   | pass      | Allen Robinson    | 14        | 3        | 21.43  |
| LA   | pass      | Cooper Kupp       | 11        | 4        | 36.36  |
| LA   | run       | Darrell Henderson | 10        | 3        | 30.0   |
| LA   | pass      | Tyler Higbee      | 9         | 0        | 0.0    |
| LA   | pass      | Brandon Powell    | 5         | 0        | 0.0    |
| LA   | run       | Malcolm Brown     | 4         | 0        | 0.0    |
| LA   | pass      | Van Jefferson     | 3         | 2        | 66.67  |
| LA   | pass      | Ben Skowronek     | 3         | 0        | 0.0    |

LA has been pretty bad as of late and don't even have that many Red Zone attempts given that Cooper Kupp hasn't played since Week 10. I'm going to look at a more recent snapshot to see if I can get a better analysis.

#### Weeks 10-14
| team | play_type | player_name       | num_plays | count_td | td_pct |
| :--- | :-------- | :---------------- | :-------- | :------- | :----- |
| LA   | run       | Cam Akers         | 6         | 3        | 50.0   |
| LA   | pass      | Van Jefferson     | 3         | 2        | 66.67  |
| LA   | pass      | Tyler Higbee      | 3         | 0        | 0.0    |
| LA   | run       | Bryce Perkins     | 2         | 0        | 0.0    |
| LA   | pass      | Allen Robinson    | 1         | 1        | 100.0  |
| LA   | run       | Darrell Henderson | 1         | 1        | 100.0  |
| LA   | pass      | Ben Skowronek     | 1         | 0        | 0.0    |
| LA   | pass      | Brandon Powell    | 1         | 0        | 0.0    |
| LA   | pass      | Brycen Hopkins    | 1         | 0        | 0.0    |
| LA   | pass      | Cam Akers         | 1         | 0        | 0.0    |

A more recent snapshot doesn't paint a clearer picture. Basically, LA doesn't get many opportunities so if you can help it, find someone else to play. Best you can do is play Cam Akers and pray for a touchdown. 