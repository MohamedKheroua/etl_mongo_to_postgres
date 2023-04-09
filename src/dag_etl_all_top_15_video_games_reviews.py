import os

import pymongo

import pandas as pd

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from sqlalchemy import create_engine
from sqlalchemy import types

import psycopg2
from configparser import ConfigParser

from airflow import DAG
from airflow.operators.python import PythonOperator

from dateutil import parser

# DAG parameters
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023,4,1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
    'provide_context': True
}

# DAG creation
# execution everyday at midnight
dag = DAG(
    'dag_etl_all_top_15_video_games_reviews',
    default_args=default_args,
    description='DAG Last 6 months video games reviews',
    schedule="0 0 * * *",
    catchup=False
)

def extract_and_load(**kwargs):
    """
    Extract data from MongoDB database (6-month past from the DAG execution date) and load it into a PostgreSQL table.
    """
    ## connection to mongodb
    # connection
    client = pymongo.MongoClient("mongodb://localhost:27017/",
                                username=os.getenv('MONGODB_USERNAME'),
                                password=os.getenv('MONGODB_PASSWORD'))
    # selecting the database
    db = client["videogamesDB"]
    # selecting the collection 
    col = db["rawdata"]

    print("Starting to extract ...")

    # Query date from the DAG execution date (timestamp)
    date = datetime.fromisoformat(str(parser.parse(kwargs['ts']))) - relativedelta(months=6)
    print("ts date = ",kwargs['ts'])
    print("query_date = ",date)

    query = {"reviewTime_Datetime": {"$gte": date}}

    mydocuments = col.find(query)

    df = pd.DataFrame(mydocuments)
    df.drop(columns=["_id"],inplace=True)
    
    ## Inserting results into PostgreSQL tables
    # read config file
    config_parser = ConfigParser()
    filename = "postgres/database.ini"
    config_parser.read(filename)
    conn_params = {}
    section = "postgresql"
    if config_parser.has_section(section):
        params = config_parser.items(section)
        print(params)
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
    
    print("Starting to load reviews table...")
    reviews_table = "last_6_months_reviews"
    df.to_sql(
        reviews_table,
        engine,
        if_exists='replace',
        dtype={"style": types.JSON})

    # Creating the aggregated table and updating it
    # each day limited to the 15 top ranked video games over the last 6 months
    print("Starting to create aggregated table...")
    
    agg_table = "Reviews_6_months_metrics"
    command="""
    CREATE TABLE IF NOT EXISTS {}
    (asin TEXT UNIQUE NOT NULL,
    mean_overall DOUBLE PRECISION NOT NULL,
    count_rating_users BIGINT NOT NULL,
    oldest_overall_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    latest_overall_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (ASIN))
    """.format(agg_table)
    try:
        # create a cursor
        cur = conn.cursor()
        cur.execute(f'{command}')
        print("Table {} created... ".format(agg_table))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    print("Starting to load data into aggregated table...")

    command="""
    INSERT INTO {0}
    SELECT
    asin,
    AVG(overall) as mean_overall,
    COUNT(DISTINCT {1}."reviewerID") as count_rating_users,
    MIN({1}."reviewTime_Datetime") as oldest_overall_date,
    MAX({1}."reviewTime_Datetime") as latest_overall_date
    FROM {1}
    WHERE verified = TRUE
    GROUP BY asin
    ORDER BY mean_overall DESC
    LIMIT 15
    ON CONFLICT (asin) DO UPDATE
    SET mean_overall = EXCLUDED.mean_overall,
    count_rating_users = EXCLUDED.count_rating_users,
    oldest_overall_date = EXCLUDED.oldest_overall_date,
    latest_overall_date = EXCLUDED.latest_overall_date;
    """.format(agg_table,reviews_table)
    try:
        # create a cursor
        cur = conn.cursor()
        cur.execute(f'{command}')
        print("Table {} created... ".format(agg_table))
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

task_extract = PythonOperator(
    task_id='extract_and_load',
    dag=dag,
    python_callable=extract_and_load
)

task_extract