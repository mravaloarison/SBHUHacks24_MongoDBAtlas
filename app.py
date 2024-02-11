from flask import Flask, request, jsonify
from os import environ as env
import openai
from flask_cors import CORS

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = env.get("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

mydb = client["interviewdb"]
mycol = mydb["descriptions"]


openai.api_key = env.get("OPENAI_API_KEY")


app = Flask(__name__)
CORS(app)


@app.route("/generate_interview", methods=["POST", "GET"])
def generate_interview():
    data = request.json
    prompt = {
        "job_title": data["job_title"],
        "job_type": data["job_type"],
        "job_description": data["job_description"],
        "industry": data["industry"],
        "location": data["location"],
    }
    print(prompt)
    completion = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt="generate a new different interview question based on this type of job: " + str(prompt),
        max_tokens=1000
    )
    print(completion.choices[0].text.strip())
    return jsonify({"response": completion.choices[0].text.strip()})


@app.route("/generate_feedback", methods=["POST", "GET"])
def generate_feedback():
    data = request.json
    # question
    question = data["question"]
    # answer
    answer = data["answer"]
    # feedback
    feedback = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt="You are a job interview of a candidate. the question that you gave to the candidatet is:\"  " + question + "\". then the candidate answer is:\" " + answer + " \". Now you have to give your feedback. keep the feed back in 35 words only.",
        max_tokens=500
    )
    
    return jsonify({"response": feedback.choices[0].text.strip()})


@app.route("/save_interview", methods=["POST", "GET"])
def save():
    data = request.json
    job_details = data.get("job_details")
    print(job_details)

    if job_details is None:
        print("error 1")
        return jsonify({"error": "No job details provided"})

    try:
        # insert into db
        mycol.insert_one(job_details)
        print("success")
        return jsonify({"response": "success"})
    except Exception as e:
        print("error 2")
        print(e)
        return jsonify({"error": str(e)})
    

@app.route("/get_interviews")
def get_interviews():
    try:
        interviews = mycol.find({}, {'_id': False})
        interviews = list(interviews)
        return interviews
    except Exception as e:
        return jsonify({"error": str(e)})