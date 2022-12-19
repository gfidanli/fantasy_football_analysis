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
GROUP BY posteam, play_type, player_name)
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