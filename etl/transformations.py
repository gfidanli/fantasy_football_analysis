"""
Perform processing on tables to create intermediary tables for further analysis.
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

import config

def pbp_scoring_summary(conn):
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
                WHERE season < {config.current_season}
            ), away_games AS (
                SELECT
                    game_id,
                    season,
                    week,
                    game_type,
                    away_team AS team,
                    away_score AS score
                FROM schedules
                WHERE season < {config.current_season}
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
                WHERE season = {config.current_season} AND week <= {config.latest_week}
            ), away_games AS (
                SELECT
                    game_id,
                    season,
                    week,
                    game_type,
                    away_team AS team,
                    away_score AS score
                FROM schedules
                WHERE season = {config.current_season} AND week <= {config.latest_week}
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
    return pd.read_sql(query, conn)

def red_zone_efficiency(conn):
    """
    This query takes the play-by-play data and filters for Red Zone (<= 20 yards till goal)
    run or pass plays. Filters out 2-PT Conversion attempts. 
    Table will be at team-play-week-player_name level so that it can be aggregated
    on a weekly basis in order to analyze both long-term and short-term trends.

    NULL values for player_name are plays that did not produce any yards: 
    interceptions, sacks, fumbles, etc.

    TD conversion for each player is calculated by aggregating the number of Red Zone
    plays for each player and dividing by number of those plays that resulted in a TD.
    """

    query = f"""
    WITH data_table AS (
        SELECT
            *,
            COUNT(*) AS num_plays,
            COUNT(CASE WHEN touchdown = 1 THEN 1 END) AS count_td
        FROM
        (
            SELECT
                week,
                posteam AS team,
                play_type,
                CASE
                    WHEN play_type = 'run' THEN rusher_player_id
                    ELSE receiver_player_id
                END AS player_id,
                touchdown
            FROM pbp
            WHERE season = 2022
                AND week <= 15
                AND yardline_100 <= 20
                AND play_type IN ('run', 'pass')
                AND two_point_attempt = 0
        )
        GROUP BY
            team,
            play_type,
            player_id,
            week
    )
    SELECT
        week,
        team,
        play_type,
        player_name,
        num_plays,
        count_td
    FROM data_table
    LEFT JOIN
    (
        -- This will ensure that there are no duplicate rows
        SELECT DISTINCT 
            player_id,
            player_display_name AS player_name
        FROM weekly
    ) AS weekly_temp
    ON weekly_temp.player_id = data_table.player_id
    -- only bring in plays that were successful (did not have to score a TD)
    WHERE player_name IS NOT NULL 
    """
    
    return pd.read_sql(query, conn)

def stack_schedules(conn):
    """
    This query converts the schedules table from the game-level (wide) to
    game-team level (long).
    """

    query = f"""
    WITH home_games AS (
        SELECT 
            game_id,
            season,
            week, 
            home_team AS team
        FROM schedules
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}
    ),
    away_games AS (
        SELECT 
            game_id,
            season,
            week, 
            away_team AS team
        FROM schedules
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}
    ),
    stacked AS (
        SELECT *
        FROM home_games
        UNION
        SELECT *
        FROM away_games
    )
    SELECT *
    FROM stacked
    """

    return pd.read_sql(query, conn)

def tableau_export(conn):
    """
    This query takes various stats and combines them into a single table
    for use in creating the NFL Season Summary Dashboard hosted at 
    https://public.tableau.com/app/profile/sergio.fidanli/viz/2022NFLSeasonSummary/QBs?publish=yes

    The query was last updated 12/10/22 in the Day 47 notebook
    """

    query = f"""
    WITH weekly_data AS (
        SELECT
            player_id,
            player_display_name AS player_name,
            position,
            recent_team,
            season,
            week,
            season_type,
            sacks,
            passing_air_yards AS pass_air_yds,
            passing_yards_after_catch AS pass_yac,
            passing_epa AS pass_epa,
            passing_2pt_conversions AS pass_2pt_conv,
            pacr,
            rushing_fumbles,
            rushing_fumbles_lost,
            rushing_epa AS rush_epa, 
            receiving_air_yards AS rec_air_yds,
            receiving_yards_after_catch AS rec_yac,
            receiving_epa AS rec_epa,
            racr,
            target_share,
            air_yards_share,
            wopr,
            fantasy_points AS fantasy_pts,
            fantasy_points_ppr AS fantasy_pts_ppr
        FROM weekly
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}
            AND position IN ('QB', 'WR', 'RB', 'TE')),
    pfr_pass_data AS (
        SELECT
            season,
            week,
            opponent,
            pfr_player_name AS player_name,
            passing_bad_throws,
            passing_bad_throw_pct,
            times_sacked,
            times_blitzed,
            times_hurried,
            times_hit,
            times_pressured,
            times_pressured_pct,
            ids.gsis_id
        FROM pfr_pass
        JOIN ids
            ON ids.pfr_id = pfr_pass.pfr_player_id
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}),
    pfr_rec_data AS (
        SELECT
            season,
            week,
            opponent,
            pfr_player_name AS player_name,
            receiving_broken_tackles,
            receiving_drop,
            receiving_drop_pct,
            receiving_int,
            receiving_rat,
            ids.gsis_id
        FROM pfr_rec
        JOIN ids
            ON ids.pfr_id = pfr_rec.pfr_player_id
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}),
    pfr_rush_data AS (
        SELECT
            season,
            week,
            opponent,
            pfr_player_name AS player_name,
            carries,
            rushing_yards_before_contact AS rush_yds_before_contact,
            rushing_yards_before_contact_avg AS rush_yds_before_contact_avg,
            rushing_yards_after_contact AS rush_yds_after_contact,
            rushing_yards_after_contact_avg AS rush_yds_after_contact_avg,
            rushing_broken_tackles AS rush_broken_tackles,
            ids.gsis_id
        FROM pfr_rush
        JOIN ids
            ON ids.pfr_id = pfr_rush.pfr_player_id
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}),
    ngs_pass_data AS (
        SELECT
            season,
            week,
            player_display_name AS player_name,
            attempts,
            pass_yards,
            pass_touchdowns AS pass_tds,
            interceptions,
            avg_time_to_throw,
            avg_completed_air_yards,
            avg_air_yards_differential,
            aggressiveness,
            max_completed_air_distance,
            avg_air_yards_to_sticks,
            passer_rating,
            completions,
            completion_percentage,
            expected_completion_percentage,
            completion_percentage_above_expectation,
            avg_air_distance,
            max_air_distance,
            player_gsis_id
        FROM ngs_pass
        WHERE season = {config.current_season}
            AND week BETWEEN 1 AND {config.latest_week}),
    ngs_rec_data AS (
        SELECT
            season,
            week,
            player_display_name AS player_name,
            avg_cushion,
            avg_separation,
            avg_intended_air_yards,
            percent_share_of_intended_air_yards,
            receptions,
            targets,
            catch_percentage,
            yards,
            rec_touchdowns,
            avg_yac,
            avg_expected_yac,
            avg_yac_above_expectation,
            player_gsis_id
        FROM ngs_rec
        WHERE season = {config.current_season}
            AND week BETWEEN 1 AND {config.latest_week}),
    ngs_rush_data AS (
        SELECT
            season,
            week,
            player_display_name AS player_name,
            efficiency,
            percent_attempts_gte_eight_defenders,
            avg_time_to_los,
            rush_attempts,
            rush_yards,
            expected_rush_yards,
            rush_yards_over_expected,
            avg_rush_yards,
            rush_yards_over_expected_per_att,
            rush_pct_over_expected,
            rush_touchdowns,
            player_gsis_id
        FROM ngs_rush
        WHERE season = {config.current_season}
            AND week BETWEEN 1 AND {config.latest_week}),
    snap_counts_data AS (
        SELECT
            season,
            week,
            player AS player_name,
            --opponent,
            offense_snaps,
            offense_pct AS offense_snaps_pct,
            defense_snaps,
            defense_pct AS defense_snaps_pct,
            st_snaps,
            st_pct AS st_snaps_pct,
            ids.gsis_id
        FROM snap_counts
        JOIN ids
            ON ids.pfr_id = snap_counts.pfr_player_id
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}),
    joined_tables AS (
        SELECT
            player_id,
            weekly_data.player_name,
            weekly_data.position,
            recent_team,
            weekly_data.season,
            weekly_data.week,
            season_type,
            sacks,
            pass_air_yds,
            pass_yac,
            pass_epa,
            pass_2pt_conv,
            pacr,
            rushing_fumbles,
            rushing_fumbles_lost,
            rush_epa, 
            rec_air_yds,
            rec_yac,
            rec_epa,
            racr,
            target_share,
            air_yards_share,
            wopr,
            fantasy_pts,
            fantasy_pts_ppr,
            passing_bad_throws,
            passing_bad_throw_pct,
            times_sacked,
            times_blitzed,
            times_hurried,
            times_hit,
            times_pressured,
            times_pressured_pct,
            receiving_broken_tackles,
            receiving_drop,
            receiving_drop_pct,
            receiving_int,
            receiving_rat,
            carries,
            rush_yds_before_contact,
            rush_yds_before_contact_avg,
            rush_yds_after_contact,
            rush_yds_after_contact_avg,
            rush_broken_tackles,
            attempts,
            pass_yards,
            pass_tds,
            interceptions,
            avg_time_to_throw,
            avg_completed_air_yards,
            avg_air_yards_differential,
            aggressiveness,
            max_completed_air_distance,
            avg_air_yards_to_sticks,
            passer_rating,
            completions,
            completion_percentage,
            expected_completion_percentage,
            completion_percentage_above_expectation,
            avg_air_distance,
            max_air_distance,
            avg_cushion,
            avg_separation,
            avg_intended_air_yards,
            percent_share_of_intended_air_yards,
            receptions,
            targets,
            catch_percentage,
            yards,
            rec_touchdowns,
            avg_yac,
            avg_expected_yac,
            avg_yac_above_expectation,
            efficiency,
            percent_attempts_gte_eight_defenders,
            avg_time_to_los,
            rush_attempts,
            rush_yards,
            expected_rush_yards,
            rush_yards_over_expected,
            avg_rush_yards,
            rush_yards_over_expected_per_att,
            rush_pct_over_expected,
            rush_touchdowns,
            offense_snaps,
            offense_snaps_pct,
            defense_snaps,
            defense_snaps_pct,
            st_snaps,
            st_snaps_pct
        FROM weekly_data
        LEFT JOIN pfr_pass_data
            ON pfr_pass_data.gsis_id = weekly_data.player_id
                AND pfr_pass_data.season = weekly_data.season
                AND pfr_pass_data.week = weekly_data.week
        LEFT JOIN pfr_rec_data
            ON pfr_rec_data.gsis_id = weekly_data.player_id
                AND pfr_rec_data.season = weekly_data.season
                AND pfr_rec_data.week = weekly_data.week
        LEFT JOIN pfr_rush_data
            ON pfr_rush_data.gsis_id = weekly_data.player_id
                AND pfr_rush_data.season = weekly_data.season
                AND pfr_rush_data.week = weekly_data.week
        LEFT JOIN ngs_pass_data
            ON ngs_pass_data.player_gsis_id = weekly_data.player_id
                AND ngs_pass_data.season = weekly_data.season
                AND ngs_pass_data.week = weekly_data.week
        LEFT JOIN ngs_rec_data
            ON ngs_rec_data.player_gsis_id = weekly_data.player_id
                AND ngs_rec_data.season = weekly_data.season
                AND ngs_rec_data.week = weekly_data.week
        LEFT JOIN ngs_rush_data
            ON ngs_rush_data.player_gsis_id = weekly_data.player_id
                AND ngs_rush_data.season = weekly_data.season
                AND ngs_rush_data.week = weekly_data.week
        LEFT JOIN snap_counts_data
            ON snap_counts_data.gsis_id = weekly_data.player_id
                AND snap_counts_data.season = weekly_data.season
                AND snap_counts_data.week = weekly_data.week
    )
    SELECT *
    FROM joined_tables
    """

    return pd.read_sql(query, conn)


def fantasy_pts_allowed(conn):
    """
    This query calculates fantasy points allowed by each team for the following
    positions: QB, RB, WR, and TE.

    The lower the rank the more points that team allows to the position.
    """

    query = f"""
    WITH fantasy_totals_by_team AS (
        -- Get the total fantasy points scored per team, per position, per week
        SELECT
            recent_team,
            position,
            week,
            ROUND(SUM(fantasy_points), 2) as tot_pts,
            ROUND(SUM(fantasy_points_ppr), 2) as tot_pts_ppr
        FROM weekly
        WHERE season = {config.current_season}
            AND week <= {config.latest_week}
            AND position in ('QB', 'RB', 'WR', 'TE')
        GROUP BY recent_team, position, week),
    -- Get schedule info
        home_games AS (
            SELECT 
                game_id,
                season,
                week, 
                home_team AS team,
                away_team AS opp_team
            FROM schedules
            WHERE season = {config.current_season}
                AND week <= {config.latest_week}
        ),
        away_games AS (
        SELECT 
                game_id,
                season,
                week, 
                away_team AS team,
                home_team AS opp_team
            FROM schedules
            WHERE season = {config.current_season}
                AND week <= {config.latest_week}
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
        SELECT
            game_id,
            season,
            stacked.week,
            team,
            opp_team,
            position,
            tot_pts,
            tot_pts_ppr
        FROM stacked
        LEFT JOIN fantasy_totals_by_team
            ON fantasy_totals_by_team.recent_team = stacked.team
            AND fantasy_totals_by_team.week = stacked.week),
    -- Only use opp_team to get the points scored scored against
    total_pts_scored_against AS (
        SELECT
            opp_team,
            position,
            SUM(tot_pts) AS tot_pts_scored_against,
            SUM(tot_pts_ppr) AS tot_pts_ppr_scored_against
        FROM joined_data
        GROUP BY opp_team, position),
    -- Utilize RANK() to get the season-level rankings
    season_rankings AS (
        SELECT
            opp_team AS team,
            position,
            RANK() OVER(PARTITION BY position ORDER BY tot_pts_scored_against DESC) AS r_pts_scored_against,
            RANK() OVER(PARTITION BY position ORDER BY tot_pts_ppr_scored_against DESC) AS r_pts_ppr_scored_against
        FROM total_pts_scored_against
        ORDER BY position, r_pts_ppr_scored_against)
    SELECT *
    FROM season_rankings
    """

    return pd.read_sql(query, conn)