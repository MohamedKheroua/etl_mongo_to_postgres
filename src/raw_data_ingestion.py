import os
import pymongo
import json
from datetime import datetime

# connection
client = pymongo.MongoClient("mongodb://localhost:27017/",
                             username=os.getenv('MONGODB_USERNAME'),
                             password=os.getenv('MONGODB_PASSWORD'))
# selecting the database
db = client["videogamesDB"]

# selecting the collection 
col = db["rawdata"]

# loading data from file
# the file is containing newline-delimited JSON (not comma-separated JSON)
data = []
with open('data/Video_Games_5.json') as file:
    for json_line in file.readlines():
        temp = json.loads(json_line)
        # adding a datetime key, useful for further aggregate operations in the pipeline job
        temp["reviewTime_Datetime"] = datetime.fromtimestamp(int(temp["unixReviewTime"]))
        data.append(temp)

# inserting data into the collection
if isinstance(data, list):
    # if inserting multiple JSON
    col.insert_many(data) 
else:
    # if inserting a single JSON
    col.insert_one(data)