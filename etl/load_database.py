import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import sqlite3
import nfl_data_py as nfl

"""
Use nfl_data_py package to extract NFL historical data.
In the various import functions, years have been specified to
return the earliest possible data.

Descriptions of the various datasets can be found in the project README.
"""

# Create database connection
conn = sqlite3.connect('./data/db/database.db')

# Season parameters
season_start = 1999
season_end = 2022

try:

    # ============================== #
    # Extract and Load into Database #
    # ============================== #
    
    print("Working on Weekly Table...")
    nfl.import_weekly_data(range(season_start, season_end+1)) \
        .to_sql('weekly', conn, index=False, if_exists='replace')

    print("Working on Seasonal Table...")
    nfl.import_seasonal_data(range(season_start,season_end+1)) \
        .to_sql('seasonal', conn, index=False, if_exists='replace')

    print("Working on Team Descriptions Table...")
    nfl.import_team_desc() \
        .to_sql('team_descriptions', conn, index=False, if_exists='replace')

    print("Working on Rosters Table...")
    nfl.import_rosters(range(season_start,season_end+1)) \
        .to_sql('rosters', conn, index=False, if_exists='replace')

    print("Working on Win Totals Table...")
    nfl.import_win_totals(range(season_start,season_end+1)) \
        .to_sql('win_totals', conn, index=False, if_exists='replace')

    print("Working on Score Lines Table...")
    nfl.import_sc_lines(range(season_start,season_end+1)) \
        .to_sql('score_lines', conn, index=False, if_exists='replace')

    print("Working on Officials Table...")
    nfl.import_officials(range(season_start,season_end+1)) \
        .to_sql('officials', conn, index=False, if_exists='replace')

    print("Working on Draft Picks Table...")
    nfl.import_draft_picks(range(season_start,season_end+1)) \
        .to_sql('draft_picks', conn, index=False, if_exists='replace')

    print("Working on Draft Values Table...")
    nfl.import_draft_values() \
        .to_sql('draft_values', conn, index=False, if_exists='replace')

    print("Working on Combine Table...")
    nfl.import_combine_data(range(season_start,season_end+1)) \
        .to_sql('combine', conn, index=False, if_exists='replace')

    print("Working on Schedules Table...")
    nfl.import_schedules(range(season_start,season_end+1)) \
        .to_sql('schedules', conn, index=False, if_exists='replace')

    print("Working on IDs Table...")
    nfl.import_ids() \
        .to_sql('ids', conn, index=False, if_exists='replace')

    print("Working on NGS Passing Table...")
    nfl.import_ngs_data('passing', range(season_start,season_end+1)) \
        .to_sql('ngs_pass', conn, index=False, if_exists='replace')

    print("Working on NGS Receiving Table...")
    nfl.import_ngs_data('receiving', range(season_start,season_end+1)) \
        .to_sql('ngs_rec', conn, index=False, if_exists='replace')

    print("Working on NGS Rushing Table...")
    nfl.import_ngs_data('rushing', range(season_start,season_end+1)) \
        .to_sql('ngs_rush', conn, index=False, if_exists='replace')

    print("Working on Injuries Table...")
    nfl.import_injuries(range(2009,season_end+1)) \
        .to_sql('injuries', conn, index=False, if_exists='replace')

    print("Working on QBR Table...")
    nfl.import_qbr(range(2006,season_end+1)) \
        .to_sql('qbr', conn, index=False, if_exists='replace')

    print("Working on PFR Passing Table...")
    nfl.import_pfr('pass', range(2019,season_end+1)) \
        .to_sql('pfr_pass', conn, index=False, if_exists='replace')

    print("Working on PFR Receiving Table...")
    nfl.import_pfr('rec', range(2019,season_end+1)) \
        .to_sql('pfr_rec', conn, index=False, if_exists='replace')

    print("Working on PFR Rushing Table...")
    nfl.import_pfr('rush', range(2019,season_end+1)) \
        .to_sql('pfr_rush', conn, index=False, if_exists='replace')

    print("Working on Snap Counts Table...")
    nfl.import_snap_counts(range(2012,season_end+1)) \
        .to_sql('snap_counts', conn, index=False, if_exists='replace')

    # ----------------- #
    # Play-By-Play Data #
    # ----------------- #
    
    print("Working on Play-By-Play table...")
    
    cols = [ 'game_id', 'season', 'week', 'season_type', 'home_team',
             'away_team', 'posteam', 'defteam', 'time', 'game_half', 'quarter_end', 
             'touchdown', 'pass_touchdown', 'rush_touchdown', 'return_touchdown', 
             'extra_point_attempt', 'extra_point_result', 'two_point_attempt', 
             'field_goal_attempt', 'field_goal_result', 'two_point_conv_result', 
             'safety', 'success', 'td_team', 'posteam_score', 'defteam_score', 
             'posteam_score_post', 'defteam_score_post', 'total_home_score', 
             'total_away_score', 'away_score', 'home_score', 'desc', 'yardline_100',
             'goal_to_go', 'yrdln', 'ydstogo', 'play_type', 'penalty', 'receiver_player_id',
             'receiver_player_name', 'receiving_yards', 'rusher_player_id', 'rusher_player_name',
             'rushing_yards']

    pbp = nfl.import_pbp_data(range(1999, 2023), cols, downcast=True, cache=False, alt_path=None)
    pbp[cols].to_sql('pbp', conn, index=False, if_exists='replace')

    # ============================== #
    #    Confirm Successful Load     #
    # ============================== #

    # Getting all tables from sqlite_master
    sql_query = """SELECT name FROM sqlite_master
    WHERE type='table';"""

    # Create cursor object
    cursor = conn.cursor()
     
    # executing our sql query
    cursor.execute(sql_query)
    print("\nList of tables:\n")
     
    # Print all tables in database
    for table in cursor.fetchall():
        print(table[0])

except Exception as e:
    print(e)

finally:
    # Close connection to database if open
    if conn:    
        conn.close()
        print("\nthe sqlite connection is closed")