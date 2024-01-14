from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from vectorSearch import vector_job_search

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['career_nav']
job_collection = db['job_descriptions_dice']
user_collection = db['users']

@app.route('/data')
def get_data():
    data = job_collection.find()  # Fetch data from MongoDB
    data_list = list(data)  # Convert cursor to list
    for item in data_list:  # Convert ObjectId to string
        item['_id'] = str(item['_id'])
    return jsonify(data_list)

@app.route('/add_user', methods=['POST'])
def add_user():
    user_data = request.json
    if not user_data:
        return jsonify({"error": "No user data provided"}), 400

    try:
        # Insert user data into MongoDB
        result = user_collection.insert_one(user_data)
        # Return the inserted ID
        return jsonify({"inserted_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_user/<userid>', methods=['GET'])
def get_user(userid):
    try:
        # Convert the userid to ObjectId for querying MongoDB
        obj_id = ObjectId(userid)
    except:
        return jsonify({"error": "Invalid user ID"}), 400

    user = user_collection.find_one({"_id": obj_id})

    if user:
        # Convert the result to JSON
        return dumps(user), 200
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route('/search_jobs', methods=['GET'])
def search_jobs():
    # Get the query from the request (e.g., as a query parameter)
    query = request.args.get('query', '')  # Default to empty string if not provided

    # Use the imported function to perform the job search
    job_postings = vector_job_search(query)

    # Return the job postings as JSON
    return jsonify(job_postings)

@app.route('/job_search')
def job_search_page():
    return render_template('index.html')

@app.route('/')
def home():
    return "Welcome to the API!"

if __name__ == '__main__':
    app.run(debug=True)