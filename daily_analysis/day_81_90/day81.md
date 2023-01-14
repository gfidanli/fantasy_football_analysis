# Day 81
Today I took the total number of Red Zone plays by playoff team and got the percentage of those that ended up in a TD. I have both the percentage over the total season and the last 4 weeks to see what teams have scoring momentum going into the playoffs.

## Query
```sql
WITH data_table AS (
	SELECT
        team,
        week,
        -- play_type,
        SUM(touchdown) OVER(PARTITION BY team, week) AS sum_rz_td,
        -- SUM(penalty) OVER(PARTITION BY team, week) AS sum_rz_penalties,
        COUNT(*) OVER (PARTITION BY team, week) AS tot_rz_plays
    FROM (
        SELECT
            season,
            week,
            posteam AS team,
            play_type,
            touchdown
            -- penalty
        FROM pbp
        WHERE season = 2022
            AND week <= 18
            AND yardline_100 <= 20
            -- AND play_type IN ('run', 'pass')
            AND two_point_attempt = 0
            AND extra_point_attempt = 0
            AND field_goal_attempt = 0
            AND posteam IN ('KC', 'BUF', 'CIN', 'JAX', 'LAC', 'BAL', 'MIA', 'PHI', 'SF', 'MIN', 'TB', 'DAL', 'NYG', 'SEA')
    )
), regular_season AS (
    SELECT
        team,
        -- 'reg_season' AS period,
        1.0 * rz_td / rz_plays AS rz_td_pct
        -- 1.0 * rz_penalties / rz_plays AS rz_penalty_pct
    FROM
    (SELECT
        team,
        AVG(sum_rz_td) AS rz_td,
        -- AVG(sum_rz_penalties) AS rz_penalties,
        AVG(tot_rz_plays) AS rz_plays
    FROM data_table
    GROUP BY team)
), last_4_wk AS (
    SELECT
        team,
        -- 'last 4 wk' AS period,
        1.0 * rz_td / rz_plays AS rz_td_pct
        -- 1.0 * rz_penalties / rz_plays AS rz_penalty_pct
    FROM
    (SELECT
        team,
        AVG(sum_rz_td) AS rz_td,
        -- AVG(sum_rz_penalties) AS rz_penalties,
        AVG(tot_rz_plays) AS rz_plays
    FROM data_table
    WHERE week BETWEEN 14 and 18
    GROUP BY team)
)
SELECT
    regular_season.team,
    -- period,
    ROUND(regular_season.rz_td_pct * 100, 2) AS rz_td_pct_reg,
    ROUND(last_4_wk.rz_td_pct * 100, 2) AS rz_td_pct_last4wk,
    ROUND(((last_4_wk.rz_td_pct  - regular_season.rz_td_pct ) / regular_season.rz_td_pct) * 100, 2) AS pct_change
    -- ROUND(rz_penalty_pct * 100, 2) AS rz_penalty_pct
FROM regular_season
LEFT JOIN last_4_wk
    ON last_4_wk.team = regular_season.team
ORDER BY rz_td_pct_last4wk DESC
;
```

## Results
| team | rz_td_pct_reg | rz_td_pct_last4wk | pct_change |
| :--- | :------------ | :---------------- | :--------- |
| KC   | 18.35         | 29.73             | 62.04      |
| NYG  | 19.36         | 25.6              | 32.21      |
| MIA  | 24.45         | 23.79             | -2.71      |
| DAL  | 24.08         | 21.48             | -10.79     |
| BUF  | 17.12         | 21.02             | 22.78      |
| JAX  | 16.14         | 20.66             | 28.02      |
| MIN  | 18.09         | 19.57             | 8.2        |
| SF   | 16.58         | 17.47             | 5.38       |
| CIN  | 17.49         | 15.21             | -13.02     |
| TB   | 12.63         | 15.02             | 18.86      |
| LAC  | 16.3          | 14.42             | -11.54     |
| PHI  | 18.02         | 13.33             | -26.02     |
| SEA  | 15.89         | 11.28             | -29.02     |
| BAL  | 14.97         | 8.13              | -45.73     |

No surprise to see KC at the top when looking at the last 4 weeks but I am surprised they weren't higher up during the regular season. Their RZ conversion percentage is actually up 62% in the last 4 weeks compared to their regular season average. 

Baltimore's RZ conversion is horrible and they've really slid from their regular season average.