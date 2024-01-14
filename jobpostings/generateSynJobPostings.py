# Step 1: Make sure the DB is working properly. Use the testDB.py before getting here.

from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')

# Access the database (create it if it doesn't exist)
db = client['career_nav']

# Access a collection in the database (create it if it doesn't exist)
collection = db['job_descriptions']

#Step 2: Generate synethetic data
import os
import openai
import json

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("AZURE_OPENAI_KEY1")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'
deployment_name = os.getenv('AZURE_DEPLOYMENT_NAME')


job_description_prompt = """
You are an HR assistant who will build synthetic data for a tool to help students train. Generate a comprehensive job description for a [Job Title, e.g., 'Senior Software Engineer'] in the [Industry, e.g., 'Technology'] sector. The job is located in [Location, e.g., 'San Francisco, CA']. Please include the following details:

CompanyOverview for Brief Company Overview:

 Give a real company name that is creative and legit (CompanyName), provide a short introduction about the company (Introduction), including its core values and mission.

Job Summary (JobSummary): There has to be a JobTitle, Location, JobOveriew(Give an overview of what the job entails and its significance to the company.

Key Responsibilities (KeyResponsibilities):

Describe in detail the day-to-day responsibilities and tasks the role involves. (DailyTasks)
Highlight any specific projects or areas of focus. (SpecificFocus)
Required Skills and Qualifications: (RequiredSkills)

List essential skills and qualifications needed for the job (Essential Skills)
Include any specific programming languages, tools, or methodologies that are relevant.
Preferred Experience:

Detail any additional experience that would be beneficial, such as industry-specific knowledge or prior roles.
Location Details:
Emphasize the location of the job in [Location, e.g., 'San Francisco, CA'].
Mention any notable aspects about working in this location (e.g., office environment, proximity to key industry hubs).
Opportunities for Growth and Development:

Describe opportunities for professional development, career advancement, and skill enhancement within the role and the company.
Company Culture and Work Environment:

Give insights into the company culture and the work environment, emphasizing aspects like teamwork, innovation, work-life balance.
Benefits and Compensation:

Provide information on the salary range, benefits, and any other compensation perks or incentives.
Application Process:

Detail the steps a candidate should follow to apply for this position.
Make sure the description is engaging, professional, and provides a clear and enticing picture of what it's like to work in this role at this location.

Return in JSON format without the ``` symbols or anything. DO NOT ADD anything outside the JSON. This should be directly parsable into a dictionary.
"""

njobs = 100
for i in range(njobs):
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[{"role": "system",
                    "content": "You are a simulation assistant for an edtech company to generate mock data to train students"},
                    {"role": "assistant", "content": job_description_prompt}]
        )

        print(response.choices[0].message.content)

    except Exception as e:
        print("An error occurred:", e)



    json_string = response.choices[0].message.content.strip('`').replace("json", "", 1).strip()
    data = json.loads(json_string)
    #print(data)

    #Insert the job description into the collection
    result = collection.insert_one(data)
    print("Inserted the ",i," th item into DB ",result.inserted_id)