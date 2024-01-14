import os
from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
import together
from typing import List

together.api_key = os.getenv('TOGETHER_API_KEY')
embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval' # model API string from Together.
mongo_password = os.getenv('MONGO_ATLAS_PWD')
client = MongoClient('mongodb+srv://career_nav:'+mongo_password+'@careernav.wu8ekwo.mongodb.net/')
db = client['career_nav']
collection = db['job_descriptions_dice'] 



def generate_embeddings(input_texts: List[str], model_api_string: str) -> List[List[float]]:
    together_client = together.Together()
    outputs = together_client.embeddings.create(
        input=input_texts,
        model=model_api_string,
    )
    return [x.embedding for x in outputs.data]

def vector_job_search(text, user_embedding=None):
    if user_embedding is None:
        query_emb = generate_embeddings([text], embedding_model_string)[0]
    else:
        query_emb = user_embedding

    results = collection.aggregate([
    {
        "$vectorSearch": {
        "queryVector": query_emb,
        "path": "embedding",  # The field where the job posting embeddings are stored
        "numCandidates": 100,  # This should be 10-20x the limit
        "limit": 10,  # The number of documents to return in the results
        "index": "vector_index",  # The index name you used for vector search
        }
    }
    ])

    job_postings = []
    for i, doc in enumerate(results):
        job_posting = {
            "id": i + 1,
            "jobTitle": doc.get("jobtitle", "N/A"),
            "company": doc.get("company", "N/A"),
            "employmentType": doc.get("employmenttype_jobstatus", "N/A"),
            "location": doc.get("joblocation_address", "N/A"),
            "description": doc.get("jobdescription", "N/A"),
            # Add other fields as needed
        }
        job_postings.append(job_posting)
    return job_postings

import openai
openai.api_key = os.getenv("AZURE_OPENAI_KEY1")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'
deployment_name = os.getenv('AZURE_DEPLOYMENT_NAME')

if __name__ == "__main__":
    print(vector_job_search("software engineer"))