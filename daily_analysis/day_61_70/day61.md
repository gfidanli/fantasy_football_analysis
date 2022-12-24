# Day 61
Today I made the following updates:

- Took the code from `Day59.md` to create a view of the `red_zone_efficiency` table and added that code to `etl/transformations.py`. In my opinion, it's better to update the table to the *weekly* level since that allows for more aggregation possibilities. Not only can I aggregate for the entire season but now I can look at recent trends by aggregating only the last 2-3 weeks for example.
- Updated the SQL query code on `Day59.md` to utilize the new `red_zone_efficiency` table at the weekly level and simplified the CTE by removing the join with the `weekly` table because it wasn't necessary.
- Added fantasy points allowed table from `Day58.ipynb` to the database by adding the code to `etl/transformations.py`. I also made sure to add the function call to `etl/etl.py`.