import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import sqlite3

import config
import db_setup
import transformations

# Create database connection
conn = sqlite3.connect('./data/db/database_test.db')

def main():
    """
    Run ETL process using functions contained in db_setup.py and transformations.py
    """

    try:

        # ============================================= #
        # Extract and Load Initial Tables into Database #
        # ============================================= #

        print("Extracting data tables using nfl_data_py package...")
        db_setup.initial_db_setup(conn)

        # ============================================= #
        #    Create New Tables Using Transformations    #
        # ============================================= #

        # ----------------------------------------- #
        # Play-By-Play Scoring Category Aggregation #
        # ----------------------------------------- #
        
        print("\nWorking on PBP Scoring Summary Table...")
        temp = transformations.pbp_scoring_summary(conn)

        print(f"Number of records: {len(temp)}")

        print("\nMismatched Scores: ")
        temp.query('sched_score != pbp_score and ~pbp_score.isnull()')

        print("\nMissing Games: ")
        print(temp.query('pbp_score.isnull()')[['game_id', 'team', 'sched_score', 'pbp_score']] \
            .sort_values('game_id'))

        # Load Temporary Table into Database
        print("\nSaving PBP Scoring Summary Table...")
        temp.to_sql('pbp_score_summary', conn, index=False, if_exists='replace')

        # ------------------- #
        # Red Zone Efficiency #
        # ------------------- #
        
        print("\nWorking on Red Zone Efficiency Table...")
        temp = transformations.red_zone_efficiency(conn)

        print(f"Number of records: {len(temp)}\n")
        print(temp.head())

        # Load Temporary Table into Database
        print("\nWorking on Red Zone Efficiency Table...")
        temp.to_sql('red_zone_efficiency', conn, index=False, if_exists='replace')

        # ----------------------------------------- #
        # Convert Schedules Table from Wide to Long #
        # ----------------------------------------- #

        print("\nWorking on Stacked Schedules Table...")
        temp = transformations.stack_schedules(conn)

        print(f"Number of records: {len(temp)}\n")
        print(temp.head())

        # Load Temporary Table into Database
        print("\nSaving Stacked Schedules Table...")
        temp.to_sql('stacked_schedules', conn, index=False, if_exists='replace')

        # --------------------------------------------- #
        # NFL Current Season Summary Export for Tableau #
        # --------------------------------------------- #

        print("\Working on NFL Current Season Summary Export for Tableau...")
        temp = transformations.tableau_export(conn)

        print(f"Number of records: {len(temp)}\n")
        print(temp.head())

        # Load Temporary Table into Database
        print("\nSaving NFL Current Season Summary Export for Tableau...")
        temp.to_sql('current_season_summary_stats', conn, index=False, if_exists='replace')

        # Export to CSV for use in Tableau Public
        temp.to_csv(f"./data/output/for_tableau_all_data_week_{config.latest_week}.csv", index=False)
        print(f"\nSaved for_tableau_all_data_week_{config.latest_week}.csv")

        # ------------------------------- #
        # Fantasy Points Allowed Rankings #
        # ------------------------------- #

        print("\nWorking on Fantasy Points Allowed Table...")
        temp = transformations.fantasy_pts_allowed(conn)

        print(f"Number of records: {len(temp)}\n")
        print(temp.head())

        # Load Temporary Table into Database
        print("\nSaving Fantasy Points Allowed Table...")
        temp.to_sql('fantasy_pts_allowed', conn, index=False, if_exists='replace')
        
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

if __name__ == "__main__":
    main()
