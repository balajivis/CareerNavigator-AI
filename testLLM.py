import os
import openai

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("AZURE_OPENAI_KEY1")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'
deployment_name = os.getenv('AZURE_DEPLOYMENT_NAME')

try:
    response = openai.ChatCompletion.create(
        engine=deployment_name,
        messages=[{"role": "system",
                   "content": "You are a simulation assistant for an edtech company to generate mock data to train students"},
                  {"role": "assistant", "content": "Hello, I am a helpful assistant. I will give you random quotes."}],
    )

    print(response.choices[0].message.content)

except Exception as e:
    print("An error occurred:", e)
