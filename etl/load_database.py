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
    
    nfl.import_weekly_data(range(season_start, season_end+1)).\
        to_sql('weekly', conn, index=False, if_exists='replace')

    nfl.import_seasonal_data(range(season_start,season_end+1)).\
        to_sql('seasonal', conn, index=False, if_exists='replace')

    nfl.import_team_desc().\
        to_sql('team_descriptions', conn, index=False, if_exists='replace')

    nfl.import_rosters(range(season_start,season_end+1)).\
        to_sql('rosters', conn, index=False, if_exists='replace')

    nfl.import_win_totals(range(season_start,season_end+1)).\
        to_sql('win_totals', conn, index=False, if_exists='replace')

    nfl.import_sc_lines(range(season_start,season_end+1)).\
        to_sql('score_lines', conn, index=False, if_exists='replace')

    nfl.import_officials(range(season_start,season_end+1)).\
        to_sql('officials', conn, index=False, if_exists='replace')

    nfl.import_draft_picks(range(season_start,season_end+1)).\
        to_sql('draft_picks', conn, index=False, if_exists='replace')

    nfl.import_draft_values().\
        to_sql('draft_values', conn, index=False, if_exists='replace')

    nfl.import_combine_data(range(season_start,season_end+1)).\
        to_sql('combine', conn, index=False, if_exists='replace')

    nfl.import_schedules(range(season_start,season_end+1)).\
        to_sql('schedules', conn, index=False, if_exists='replace')

    nfl.import_ids().\
        to_sql('ids', conn, index=False, if_exists='replace')

    nfl.import_ngs_data('passing', range(season_start,season_end+1)).\
        to_sql('ngs_pass', conn, index=False, if_exists='replace')

    nfl.import_ngs_data('receiving', range(season_start,season_end+1)).\
        to_sql('ngs_rec', conn, index=False, if_exists='replace')

    nfl.import_ngs_data('rushing', range(season_start,season_end+1)).\
        to_sql('ngs_rush', conn, index=False, if_exists='replace')

    nfl.import_injuries(range(2009,season_end+1)).\
        to_sql('injuries', conn, index=False, if_exists='replace')

    nfl.import_qbr(range(2006,season_end+1)).\
        to_sql('qbr', conn, index=False, if_exists='replace')

    nfl.import_pfr('pass', range(2019,season_end+1)).\
        to_sql('pfr_pass', conn, index=False, if_exists='replace')

    nfl.import_pfr('rec', range(2019,season_end+1)).\
        to_sql('pfr_rec', conn, index=False, if_exists='replace')

    nfl.import_pfr('rush', range(2019,season_end+1)).\
        to_sql('pfr_rush', conn, index=False, if_exists='replace')

    nfl.import_snap_counts(range(2012,season_end+1)).\
        to_sql('snap_counts', conn, index=False, if_exists='replace')

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