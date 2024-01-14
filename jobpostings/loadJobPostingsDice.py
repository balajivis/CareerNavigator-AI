import pandas as pd
df = pd.read_csv('dice_com-job_us_sample.csv')
data_dict = df.to_dict('records')

import os
from dotenv import load_dotenv
load_dotenv()

# Insert into MongoDB
from pymongo import MongoClient
#client = MongoClient('mongodb://localhost:27017/')
mongo_password = os.getenv('MONGO_ATLAS_PWD')
client = MongoClient('mongodb+srv://career_nav:'+mongo_password+'@careernav.wu8ekwo.mongodb.net/')
db = client['career_nav'] # Access the database (create it if it doesn't exist)


collection = db['job_descriptions_dice'] # Access a collection in DB (create it if it doesn't exist)

collection.insert_many(data_dict)