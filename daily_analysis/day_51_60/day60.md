# Day 60
Instead of writing a SQL query or doing some analysis in a Jupyter Notebook, I decided to refactor my ETL (Extract, Transform, Load) process for my database.  

Originally, I had two scripts:
1. `load_database.py`
2. `process_tables.py`

The flow was simple, run `load_database.py` to make an api call and save each table to the database. The thing is, each API call had multiple parameters and everything was hard-coded in the script. If I wanted to change a date range for one or a subset of tables I would have to manually code it and things would get messy, quickly. Plus it wasn't easy to see which tables contained which dates (or seasons in this case).  

Next I run `process_tables.py` which runs multiple queries on the database and creates new tables that make it easier to run specific analysis. I need these tables so that future SQL queries can be simplified. This script needed to be refactored to utilize functions and there's the problem of parameters being hard-coded in the script.  

So, I made the following scripts:
1. `config.py`: holds parameters for the ETL process
2. `db_setup.py`: function for initial API call to populate database
3. `transformations.py`: functions that transform base tables into new tables
4. `etl.py`: main script and the only one that **needs** to be run

With this new process, a user only needs to make changes to the `config.py` script and can then replicate the database.

