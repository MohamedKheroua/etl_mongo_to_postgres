import pymongo

import pandas as pd

import os

from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy import create_engine
from sqlalchemy import types

import psycopg2
from configparser import ConfigParser

## connection to mongodb
# connection
client = pymongo.MongoClient("mongodb://localhost:27017/",
                             username=os.getenv('MONGODB_USERNAME'),
                             password=os.getenv('MONGODB_PASSWORD'))
# selecting the database
db = client["videogamesDB"]
# selecting the collection 
col = db["rawdata"]

## querying the database to retrieve the last 6 months reviews
temp_time = "2018-12-25T02:00:00.000Z"

parsed_date=datetime.strptime(temp_time, "%Y-%m-%dT%H:%M:%S.%fZ")
query_date = parsed_date + relativedelta(months=-6)
query = {"reviewTime_Datetime": {"$gte": query_date}}

print("Starting to extract ...")
mydocuments = col.find(query)

#to do : process data with Spark dataframe instead
df = pd.DataFrame(mydocuments)
df.drop(columns=["_id"],inplace=True)


## Inserting results into PostgreSQL tables
# read config file
parser = ConfigParser()
filename = "postgres/database.ini"
parser.read(filename)
conn_params = {}
section = "postgresql"
if parser.has_section(section):
    params = parser.items(section)
    for param in params:
        if os.environ.get(param[1])==None:
            conn_params[param[0]] = param[1].split('"')[1]
        else:
            conn_params[param[0]] = os.environ.get(param[1])
else:
    raise Exception('Section {0} not found in the {1} file'.format(section, filename))

engine = create_engine('postgresql://' + conn_params["user"] +
                       ':' + conn_params["password"] +
                       '@' + conn_params["host"] +
                       ':5432/' + conn_params["dbname"])

# Creating the last 6 months reviews table
# dropping the aggregated view first, if exists
try:
    # connect to the PostgreSQL server
    conn = psycopg2.connect(**conn_params)
    #Setting auto commit false
    conn.autocommit = True
except (Exception, psycopg2.DatabaseError) as error:
    print(error)

agg_view = "Reviews_6_months_metrics"
command = """DROP VIEW IF EXISTS {} CASCADE;""".format(agg_view)
try:
    # create a cursor
    cur = conn.cursor()
    cur.execute(f'{command}')
    print("View {} dropped... ".format(agg_view))
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)

print("Starting to load reviews table...")
reviews_table = "last_6_months_reviews"
df.to_sql(
    reviews_table,
    engine,
    if_exists='replace',
    dtype={"style": types.JSON})

# Creating the aggregated view
# limit to the 15 top ranked viedeo games
print("Starting to create aggregated view...")

query_Reviews_6_months_metrics="""
SELECT
asin,
AVG(overall) as mean_overall,
COUNT(DISTINCT {0}."reviewerID") as count_rating_users,
MIN({0}."reviewTime_Datetime") as oldest_overall_date,
MAX({0}."reviewTime_Datetime") as latest_overall_date
FROM {0}
WHERE verified = TRUE
GROUP BY asin
ORDER BY mean_overall DESC
LIMIT 15
""".format(reviews_table)

command ="""
CREATE OR REPLACE VIEW {} as {}
""".format(agg_view,query_Reviews_6_months_metrics)

try:
    # create a cursor
    cur = conn.cursor()
    cur.execute(f'{command}')
    print("View {} created... ".format(agg_view))
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)

# closing connection
try:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
except (Exception, psycopg2.DatabaseError) as error:
    print(error)