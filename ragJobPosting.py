import os
from dotenv import load_dotenv
import together
from pymongo import MongoClient
from tqdm import tqdm
import time 

load_dotenv()
together.api_key = os.getenv('TOGETHER_API_KEY')
mongo_password = os.getenv('MONGO_ATLAS_PWD')
client = MongoClient('mongodb+srv://career_nav:'+mongo_password+'@careernav.wu8ekwo.mongodb.net/')

from typing import List

def generate_embeddings(input_texts: List[str], model_api_string: str) -> List[List[float]]:
    """Generate embeddings from Together python library.

    Args:
        input_texts: a list of string input texts.
        model_api_string: str. An API string for a specific embedding model of your choice.

    Returns:
        embeddings_list: a list of embeddings. Each element corresponds to the each input text.
    """
    together_client = together.Together()
    outputs = together_client.embeddings.create(
        input=input_texts,
        model=model_api_string,
    )
    return [x.embedding for x in outputs.data]

embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
vector_database_field_name = 'embedding_together_m2-bert-8k-retrieval' # define your embedding field name.
NUM_DOC_LIMIT = 1000 # the number of documents you will process and generate embeddings.

sample_output = generate_embeddings(["This is a test."], embedding_model_string)
print(f"Embedding size is: {str(len(sample_output[0]))}")

db = client['career_nav'] # Access the database (create it if it doesn't exist)
collection = db['job_descriptions_dice'] # Access a collection in DB (create it if it doesn't exist)
keys_to_extract = ["company", "employmenttype_jobstatus", "joblocation_address", "jobtitle", "jobdescription"]
vector_database_field_name = "embedding"  # Field name for the embedding in MongoDB

for doc in tqdm(collection.find({}).limit(NUM_DOC_LIMIT), desc="Document Processing "):
    time.sleep(2) # wait for 2 seconds to avoid rate limit
    # Combine the selected fields into a single string
    extracted_str = "\n".join([k + ": " + str(doc[k]) for k in keys_to_extract if k in doc])
    
    # Check if embedding already exists, if not, generate and update
    if vector_database_field_name not in doc:
        doc[vector_database_field_name] = generate_embeddings(extracted_str, embedding_model_string)

    # Replace the document in MongoDB with the updated one
    collection.replace_one({'_id': doc['_id']}, doc)

