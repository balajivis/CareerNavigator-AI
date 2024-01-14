#Make sure you start the Mongoserver:
# 1. Install MongoDB
# 2. mkdir -p ~/data/d
# 3. chown -R `id -un` ~/data/db
# 4. mongod --port 27017 --dbpath ~/data/db

from pymongo import MongoClient
#client = MongoClient('mongodb://localhost:27017/')

import os
from dotenv import load_dotenv
load_dotenv()
mongo_password = os.getenv('MONGO_ATLAS_PWD')
client = MongoClient('mongodb+srv://career_nav:'+mongo_password+'@careernav.wu8ekwo.mongodb.net/')

# Access the database (create it if it doesn't exist)
db = client['career_nav']

# Access a collection in the database (create it if it doesn't exist)
collection = db['job_descriptions_dice']

documents = collection.find({}, {'_id': 0, 'jobdescription': 1})

for doc in documents:
    print(doc)