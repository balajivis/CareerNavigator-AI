from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import PyPDF2


from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from vectorSearch import vector_job_search, generate_embeddings

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'pdf'}
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['career_nav']
job_collection = db['job_descriptions_dice']
user_collection = db['users']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in range(len(reader.pages)):
                text += " "+reader.pages[page].extract_text()
    return text

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

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return redirect(request.url)
    file = request.files['resume']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('/tmp', filename)
        file.save(filepath)
        extracted_text = extract_text_from_pdf(filepath)
        print(extracted_text)
        user_embedding = generate_embeddings(extracted_text, 'togethercomputer/m2-bert-80M-8k-retrieval')
        job_postings = vector_job_search("", user_embedding=user_embedding[0])
        return jsonify(job_postings)


@app.route('/')
def home():
    return "Welcome to the API!"

if __name__ == '__main__':
    app.run(debug=True)