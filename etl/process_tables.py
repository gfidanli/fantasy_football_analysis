import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import sqlite3
import nfl_data_py as nfl

"""
Perform processing on tables to create intermediary tables for further analysis.
"""

# Create database connection
conn = sqlite3.connect('./data/db/database.db')

# Get parameters
current_season = input("Enter current season: ")
latest_week = input("Enter last full week of games: ")

# ========================================= #
# Play-By-Play Scoring Category Aggregation #
# ========================================= #
"""
This query aggregates the Play-By-Play table to calculate the score for 
each game-team combination and has a column for each scoring category.

There is a join with the schedules table to check the manual calculation 
for score and the number of game-team records that are missing (if any).
"""

query = f"""
WITH pbp_summary AS (
    WITH all_games AS (
        SELECT DISTINCT game_id, season, week, season_type, posteam AS team
        FROM pbp
        WHERE team IS NOT NULL
            AND team <> ''
        ORDER BY game_id),
    offense AS (
        SELECT
        game_id,
        posteam AS team,
        SUM(pass_touchdown) AS tot_pass_tds,
        SUM(rush_touchdown) AS tot_rush_tds
        FROM pbp
        WHERE team IS NOT NULL and team <> ''
        GROUP BY game_id, team),
    ret_tds AS (
        SELECT 
            game_id, 
            td_team AS team,
            SUM(return_touchdown) AS tot_ret_tds
        FROM pbp
        WHERE return_touchdown = 1 AND td_team = posteam
        GROUP BY game_id, team), 
    extra_pts AS (
        SELECT
            game_id,
            posteam AS team,
            COUNT(*) AS tot_extra_pts
        FROM pbp
        WHERE extra_point_attempt = 1 AND extra_point_result = 'good'
        GROUP BY game_id, posteam),
    field_goals AS (
        SELECT 
            game_id,
            -- Correct for data error in game_id: 2000_11_OAK_DEN
            CASE WHEN game_id = '2000_11_OAK_DEN' 
                AND desc LIKE '%J.Elam%' 
                AND desc LIKE '%field goal%' 
                THEN 'DEN'
            ELSE posteam
            END AS team,
            COUNT(*) AS tot_fgs
        FROM pbp
        WHERE field_goal_attempt = 1 
            AND field_goal_result = 'made'
            AND desc LIKE '%field goal%'
        GROUP BY game_id, team), 
    two_pt_convs AS (
        SELECT 
            game_id,
            posteam AS team,
            COUNT(*) AS tot_2pt_conv
        FROM pbp
        WHERE two_point_attempt = 1 AND two_point_conv_result = 'success'
        GROUP BY game_id, posteam),
    -- Counts defensive TDs and punt/kickoff return TDs
    defense AS (
        SELECT
            game_id,
            td_team AS team,
            COUNT(*) AS tot_def_tds
        FROM pbp
        WHERE touchdown = 1
            AND (
                defteam_score_post <> defteam_score
                OR (defteam_score IS NULL AND defteam_score_post >= 6)
            )
        GROUP BY game_id, td_team),
    safeties AS (
        SELECT
            game_id,
            CASE WHEN defteam_score_post <> defteam_score THEN defteam
            ELSE posteam
            END AS team,
            COUNT(*) AS tot_safeties
        FROM pbp
        WHERE safety = 1
        GROUP BY game_id, team),
    def_2pt_att AS (
        SELECT
            game_id,
            defteam AS team,
            COUNT(*) AS tot_def_2pt
        FROM pbp
        WHERE desc LIKE '%DEFENSIVE TWO-POINT ATTEMPT%'
            AND defteam_score_post <> defteam_score
        GROUP BY game_id, team),
    off_fumb_recovery AS (
        SELECT
            game_id,
            posteam AS team,
            COUNT(*) AS tot_off_fumble_recov_td
        FROM pbp
        WHERE desc LIKE '%fumble%'
            AND posteam_score_post <> posteam_score
            AND touchdown = 1
            AND pass_touchdown = 0
            AND rush_touchdown = 0
            AND return_touchdown = 0
        GROUP BY game_id, team),
    joined AS (
        SELECT 
            all_games.*,
            -- offense.*,
            CASE WHEN tot_pass_tds IS NULL THEN 0
            ELSE tot_pass_tds
            END AS tot_pass_tds,
            CASE WHEN tot_rush_tds IS NULL THEN 0
            ELSE tot_rush_tds
            END AS tot_rush_tds,
            CASE WHEN tot_ret_tds IS NULL THEN 0
            ELSE tot_ret_tds
            END AS tot_ret_tds,
            CASE WHEN tot_extra_pts IS NULL THEN 0
            ELSE tot_extra_pts
            END AS tot_extra_pts,
            CASE WHEN tot_fgs IS NULL THEN 0
            ELSE tot_fgs
            END AS tot_fgs,
            CASE WHEN tot_2pt_conv IS NULL THEN 0
            ELSE tot_2pt_conv
            END AS tot_2pt_conv,
            CASE WHEN tot_def_tds IS NULL THEN 0
            ELSE tot_def_tds
            END AS tot_def_tds,
            CASE WHEN tot_safeties IS NULL THEN 0
            ELSE tot_safeties
            END AS tot_safeties,
            CASE WHEN tot_def_2pt IS NULL THEN 0
            ELSE tot_def_2pt
            END AS tot_def_2pt,
            CASE WHEN tot_off_fumble_recov_td IS NULL THEN 0
            ELSE tot_off_fumble_recov_td
            END AS tot_off_fumble_recov_td
        FROM all_games
        LEFT JOIN offense
            ON offense.game_id = all_games.game_id
                AND offense.team = all_games.team
        LEFT JOIN ret_tds
            ON ret_tds.game_id = all_games.game_id
                AND ret_tds.team = all_games.team  
        LEFT JOIN extra_pts
            ON extra_pts.game_id = all_games.game_id
                AND extra_pts.team = all_games.team
        LEFT JOIN field_goals
            ON field_goals.game_id = all_games.game_id
                AND field_goals.team = all_games.team
        LEFT JOIN two_pt_convs
            ON two_pt_convs.game_id = all_games.game_id
                AND two_pt_convs.team = all_games.team
        LEFT JOIN defense
            ON defense.game_id = all_games.game_id
                AND defense.team = all_games.team
        LEFT JOIN safeties
            ON safeties.game_id = all_games.game_id
                AND safeties.team = all_games.team
        LEFT JOIN def_2pt_att
            ON def_2pt_att.game_id = all_games.game_id
                AND def_2pt_att.team = all_games.team
        LEFT JOIN off_fumb_recovery
            ON off_fumb_recovery.game_id = all_games.game_id
                AND off_fumb_recovery.team = all_games.team
    )
    SELECT *,
        (tot_pass_tds * 6
        + tot_rush_tds * 6
        + tot_ret_tds * 6
        + tot_extra_pts * 1
        + tot_fgs * 3
        + tot_2pt_conv * 2
        + tot_def_tds * 6
        + tot_safeties * 2
        + tot_def_2pt * 2
        + tot_off_fumble_recov_td * 6) AS score,
        -- Use old team abbrev. that matches game_id for teams that moved (pbp data has new names)
        CASE
            WHEN game_id LIKE '%OAK%' AND team = 'LV' THEN 'OAK'
            WHEN game_id LIKE '%SD%' AND team = 'LAC' THEN 'SD'
            WHEN game_id LIKE '%STL%' AND team = 'LA' THEN 'STL'
            ELSE team
        END AS team_fixed
    FROM joined
), sched AS (
    WITH sched_historical AS (
        WITH home_games AS (
            SELECT
                game_id,
                season,
                week,
                game_type,
                home_team AS team,
                home_score AS score
            FROM schedules
            WHERE season < {current_season}
        ), away_games AS (
            SELECT
                game_id,
                season,
                week,
                game_type,
                away_team AS team,
                away_score AS score
            FROM schedules
            WHERE season < {current_season}
        )
        -- Stack the data
        SELECT *
        FROM home_games
        UNION ALL
        SELECT *
        FROM away_games
    ), sched_2022 AS (
        WITH home_games AS (
            SELECT
                game_id,
                season,
                week,
                game_type,
                home_team AS team,
                home_score AS score
            FROM schedules
            WHERE season = {current_season} AND week <= {latest_week}
        ), away_games AS (
            SELECT
                game_id,
                season,
                week,
                game_type,
                away_team AS team,
                away_score AS score
            FROM schedules
            WHERE season = {current_season} AND week <= {latest_week}
        )
        SELECT *
        FROM home_games
        UNION ALL
        SELECT *
        FROM away_games
    )
    SELECT *
    FROM sched_historical
    UNION ALL
    SELECT *
    FROM sched_2022
)
SELECT
    sched.game_id,
    sched.team,
    sched.score AS sched_score,
    pbp_summary.score AS pbp_score,
    (sched.score - pbp_summary.score) AS score_diff,
    tot_pass_tds,
    tot_rush_tds,
    tot_ret_tds,
    tot_extra_pts,
    tot_fgs,
    tot_2pt_conv,
    tot_def_tds,
    tot_safeties,
    tot_def_2pt,
    tot_off_fumble_recov_td
FROM sched
LEFT JOIN pbp_summary
    ON pbp_summary.game_id = sched.game_id
    AND pbp_summary.team_fixed = sched.team
"""

temp = pd.read_sql(query, conn)
print(f"Number of records: {len(temp)}")

print("\nMismatched Scores: ")
temp.query('sched_score != pbp_score and ~pbp_score.isnull()')

print("\nMissing Games: ")
print(temp.query('pbp_score.isnull()')[['game_id', 'team', 'sched_score', 'pbp_score']] \
    .sort_values('game_id'))

# Load Summary Table into Database
print("\nSaving PBP Scoring Summary Table...")
temp.to_sql('pbp_score_summary', conn, index=False, if_exists='replace')

# ========================================= #
#                  Finish                   #
# ========================================= #

# Close connection to database if open
if conn:    
    conn.close()
    print("\nthe sqlite connection is closed")