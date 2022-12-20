# Day 57
Today's update is going to be a slight variation of yesterday's work. I'm going to use the same basic query but tweak it slightly to account for Two Point attempts. I didn't realize that these plays are run from the opponent's 2-yard line so they technically count as End Zone plays. Since I'm trying to calculate **touchdown** efficiency, it doesn't make sense to count these attempts.

I also wanted to run an update to account for Week 15 games finishing and add a `num` field to make it easier to read the table.

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
        AND week <= 15
        AND yardline_100 <= 20
        AND play_type IN ('run', 'pass')
        AND two_point_attempt = 0
)
SELECT  ROW_NUMBER() OVER() AS num -- Easier to see ranking
       ,*
FROM
(
	SELECT  *
	       ,ROUND((1.0 * count_td / num_plays) * 100,2) AS td_pct
	FROM
	(
		SELECT  posteam                                   AS team
		       ,play_type
		       ,player_name
		       ,COUNT(*)                                  AS num_plays
		       ,COUNT(CASE WHEN touchdown = 1 THEN 1 END) AS count_td
		FROM data_table
		LEFT JOIN
		( -- This will ensure that there are no duplicate rows
			SELECT  DISTINCT player_id
			       ,player_display_name AS player_name
			FROM weekly
		) AS weekly_temp
		ON weekly_temp.player_id = data_table.player_id
		GROUP BY  team
		         ,play_type
		         ,player_name
	)
	ORDER BY num_plays DESC, td_pct DESC
	LIMIT 20
)
;
```

## Top 20 By Red Zone Volume Through Week 15
| num | team | play_type | player_name      | num_plays | count_td | td_pct |
| :-- | :--- | :-------- | :--------------- | :-------- | :------- | :----- |
| 1   | DET  | run       | Jamaal Williams  | 46        | 13       | 28.26  |
| 2   | PHI  | run       | Jalen Hurts      | 41        | 11       | 26.83  |
| 3   | TEN  | run       | Derrick Henry    | 39        | 11       | 28.21  |
| 4   | PHI  | run       | Miles Sanders    | 38        | 10       | 26.32  |
| 5   | CLE  | run       | Nick Chubb       | 38        | 9        | 23.68  |
| 6   | CIN  | run       | Joe Mixon        | 37        | 6        | 16.22  |
| 7   | MIN  | run       | Dalvin Cook      | 37        | 6        | 16.22  |
| 8   | JAX  | run       | Travis Etienne   | 37        | 4        | 10.81  |
| 9   | NYG  | run       | Saquon Barkley   | 36        | 8        | 22.22  |
| 10  | LV   | run       | Josh Jacobs      | 35        | 9        | 25.71  |
| 11  | LAC  | run       | Austin Ekeler    | 35        | 8        | 22.86  |
| 12  | SEA  | run       | Kenneth Walker   | 35        | 7        | 20.0   |
| 13  | HOU  | run       | Dameon Pierce    | 33        | 3        | 9.09   |
| 14  | DAL  | run       | Ezekiel Elliott  | 32        | 10       | 31.25  |
| 15  | BUF  | run       | Devin Singletary | 32        | 4        | 12.5   |
| 16  | IND  | run       | Jonathan Taylor  | 32        | 3        | 9.38   |
| 17  | CAR  | run       | D'Onta Foreman   | 31        | 4        | 12.9   |
| 18  | CHI  | run       | David Montgomery | 30        | 5        | 16.67  |
| 19  | KC   | pass      | Travis Kelce     | 29        | 10       | 34.48  |
| 20  | PIT  | run       | Najee Harris     | 29        | 6        | 20.69  |

To check consistency I'm going to run the query for Weeks 11-15:

## Top 20 By Red Zone Volume Weeks 11-15:
| num | team | play_type | player_name           | num_plays | count_td | td_pct |
| :-- | :--- | :-------- | :-------------------- | :-------- | :------- | :----- |
| 1   | DAL  | run       | Ezekiel Elliott       | 20        | 6        | 30.0   |
| 2   | LAC  | run       | Austin Ekeler         | 18        | 3        | 16.67  |
| 3   | MIN  | run       | Dalvin Cook           | 18        | 2        | 11.11  |
| 4   | DET  | run       | Jamaal Williams       | 16        | 5        | 31.25  |
| 5   | BUF  | run       | Devin Singletary      | 16        | 2        | 12.5   |
| 6   | KC   | run       | Isiah Pacheco         | 16        | 2        | 12.5   |
| 7   | IND  | run       | Jonathan Taylor       | 15        | 2        | 13.33  |
| 8   | PHI  | run       | Jalen Hurts           | 14        | 5        | 35.71  |
| 9   | TEN  | run       | Derrick Henry         | 14        | 3        | 21.43  |
| 10  | CAR  | run       | D'Onta Foreman        | 14        | 0        | 0.0    |
| 11  | CIN  | run       | Samaje Perine         | 13        | 2        | 15.38  |
| 12  | DET  | run       | D'Andre Swift         | 13        | 2        | 15.38  |
| 13  | LV   | run       | Josh Jacobs           | 13        | 2        | 15.38  |
| 14  | GB   | run       | Aaron Jones           | 13        | 0        | 0.0    |
| 15  | PHI  | run       | Miles Sanders         | 12        | 4        | 33.33  |
| 16  | KC   | pass      | Travis Kelce          | 11        | 2        | 18.18  |
| 17  | PIT  | run       | Najee Harris          | 10        | 5        | 50.0   |
| 18  | CHI  | run       | David Montgomery      | 10        | 3        | 30.0   |
| 19  | DAL  | run       | Tony Pollard          | 10        | 2        | 20.0   |
| 20  | ATL  | run       | Cordarrelle Patterson | 10        | 1        | 10.0   |

Finally I'll look into the last two weeks:

## Top 20 By Red Zone Volume Weeks 14-15:
| num | team | play_type | player_name     | num_plays | count_td | td_pct |
| :-- | :--- | :-------- | :-------------- | :-------- | :------- | :----- |
| 1   | DAL  | run       | Ezekiel Elliott | 12        | 2        | 16.67  |
| 2   | LAC  | run       | Austin Ekeler   | 9         | 2        | 22.22  |
| 3   | TEN  | run       | Derrick Henry   | 8         | 2        | 25.0   |
| 4   | CAR  | run       | D'Onta Foreman  | 8         | 0        | 0.0    |
| 5   | IND  | run       | Zack Moss       | 8         | 0        | 0.0    |
| 6   | JAX  | run       | Travis Etienne  | 8         | 0        | 0.0    |
| 7   | CIN  | pass      | Ja'Marr Chase   | 7         | 2        | 28.57  |
| 8   | MIN  | run       | Dalvin Cook     | 7         | 1        | 14.29  |
| 9   | CIN  | run       | Joe Mixon       | 7         | 0        | 0.0    |
| 10  | TB   | pass      | Russell Gage    | 6         | 3        | 50.0   |
| 11  | PIT  | run       | Najee Harris    | 6         | 2        | 33.33  |
| 12  | CLE  | pass      | David Njoku     | 6         | 1        | 16.67  |
| 13  | DAL  | run       | Tony Pollard    | 6         | 1        | 16.67  |
| 14  | LV   | run       | Josh Jacobs     | 6         | 1        | 16.67  |
| 15  | PHI  | run       | Miles Sanders   | 6         | 1        | 16.67  |
| 16  | GB   | run       | A.J. Dillon     | 5         | 2        | 40.0   |
| 17  | MIN  | pass      | K.J. Osborn     | 5         | 2        | 40.0   |
| 18  | CAR  | run       | Chuba Hubbard   | 5         | 1        | 20.0   |
| 19  | LAC  | run       | Joshua Kelley   | 5         | 1        | 20.0   |
| 20  | DET  | run       | Jamaal Williams | 5         | 0        | 0.0    |

As a Tony Pollard owner I'm extremely disappointed by the Zeke dominance but what can you do. Zach Moss and D'Onta Foreman look like a great pickups for Week 16. They both have high Red Zone usage in the last two weeks and have yet to see a TD. In fact, D'Onta Foreman has 14 Red Zone runs in the past month without a TD. Definitely a candidate for positive TD regression.

## ETL Update
I think this table and variations of it is a great tool for Fantasy Football analysis so I'm going to add it to my `process_tables.py` script located in `root/etl/`. That way queries can be simplified going forward.  

The new table will be called red_zone_td_efficiency and will be an easy way to get a players current TD efficiency percentage through the latest week of the season.

