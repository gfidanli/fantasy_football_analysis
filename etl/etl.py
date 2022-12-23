import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import sqlite3
import nfl_data_py as nfl
import config

"""
Use nfl_data_py package to extract NFL historical data.
In the various import functions, years have been specified to
return the earliest possible data.

Descriptions of the various datasets can be found in the project README.
"""

# Create database connection
conn = sqlite3.connect('./data/db/database_test.db')

try:

    # ============================================= #
    # Extract and Load Initial Tables into Database #
    # ============================================= #

    print("Working on Weekly Table...")
    nfl.import_weekly_data(config.weekly_config['date_range']) \
        .to_sql(config.weekly_config['name'], conn, index=False, if_exists='replace')

    print("Working on Seasonal Table...")
    nfl.import_seasonal_data(config.seasonal_config['date_range']) \
        .to_sql(config.seasonal_config['name'], conn, index=False, if_exists='replace')

    print("Working on Team Descriptions Table...")
    nfl.import_team_desc() \
        .to_sql(config.team_desc_config['name'], conn, index=False, if_exists='replace')

    print("Working on Rosters Table...")
    nfl.import_rosters(config.rosters_config['date_range']) \
        .to_sql(config.rosters_config['name'], conn, index=False, if_exists='replace')

    print("Working on Win Totals Table...")
    nfl.import_win_totals(config.win_totals_config['date_range']) \
        .to_sql(config.win_totals_config['name'], conn, index=False, if_exists='replace')

    print("Working on Score Lines Table...")
    nfl.import_sc_lines(config.score_lines_config['date_range']) \
        .to_sql(config.score_lines_config['name'], conn, index=False, if_exists='replace')

    print("Working on Officials Table...")
    nfl.import_officials(config.officials_config['date_range']) \
        .to_sql(config.officials_config['name'], conn, index=False, if_exists='replace')

    print("Working on Draft Picks Table...")
    nfl.import_draft_picks(config.draft_picks_config['date_range']) \
        .to_sql(config.draft_picks_config['name'], conn, index=False, if_exists='replace')

    print("Working on Draft Values Table...")
    nfl.import_draft_values() \
        .to_sql(config.draft_values_config['name'], conn, index=False, if_exists='replace')

    print("Working on Combine Table...")
    nfl.import_combine_data(config.combine_config['date_range']) \
        .to_sql(config.combine_config['name'], conn, index=False, if_exists='replace')

    print("Working on Schedules Table...")
    nfl.import_schedules(config.schedules_config['date_range']) \
        .to_sql(config.schedules_config['name'], conn, index=False, if_exists='replace')

    print("Working on IDs Table...")
    nfl.import_ids() \
        .to_sql(config.ids_config['name'], conn, index=False, if_exists='replace')

    print("Working on NGS Passing Table...")
    nfl.import_ngs_data(config.ngs_passing_config['type'], config.ngs_passing_config['date_range']) \
        .to_sql(config.ngs_passing_config['name'], conn, index=False, if_exists='replace')

    print("Working on NGS Receiving Table...")
    nfl.import_ngs_data(config.ngs_receiving_config['type'], config.ngs_receiving_config['date_range']) \
        .to_sql(config.ngs_receiving_config['name'], conn, index=False, if_exists='replace')

    print("Working on NGS Rushing Table...")
    nfl.import_ngs_data(config.ngs_rushing_config['type'], config.ngs_rushing_config['date_range']) \
        .to_sql(config.ngs_rushing_config['name'], conn, index=False, if_exists='replace')

    print("Working on Injuries Table...")
    nfl.import_injuries(config.injuries_config['date_range']) \
        .to_sql(config.injuries_config['name'], conn, index=False, if_exists='replace')

    print("Working on QBR Table...")
    nfl.import_qbr(config.qbr_config['date_range']) \
        .to_sql(config.qbr_config['name'], conn, index=False, if_exists='replace')

    print("Working on PFR Passing Table...")
    nfl.import_pfr(config.pfr_passing_config['type'], config.pfr_passing_config['date_range']) \
        .to_sql(config.pfr_passing_config['name'], conn, index=False, if_exists='replace')

    print("Working on PFR Receiving Table...")
    nfl.import_pfr(config.pfr_receiving_config['type'], config.pfr_receiving_config['date_range']) \
        .to_sql(config.pfr_receiving_config['name'], conn, index=False, if_exists='replace')

    print("Working on PFR Rushing Table...")
    nfl.import_pfr(config.pfr_rushing_config['type'], config.pfr_rushing_config['date_range']) \
        .to_sql(config.pfr_rushing_config['name'], conn, index=False, if_exists='replace')

    print("Working on Snap Counts Table...")
    nfl.import_snap_counts(config.snap_counts_config['date_range']) \
        .to_sql(config.snap_counts_config['name'], conn, index=False, if_exists='replace')

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
