from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import requests
import csv

app = Flask(__name__)
CORS(app)

DOCUMENTS_DIR = "./documents"
RESPONSES_FILE = "responses.csv"
AWS_BEDROCK_REGION = "us-east-1"  # Change to your AWS region
AWS_BEDROCK_MODEL_ID = "arn:aws:bedrock:us-east-1:655276615738:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # Change to your AWS Bedrock model ID

# Load questions from JSON
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

def read_document(filepath):
    """Read a document's contents."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

import boto3

def query_aws_bedrock(prompt):
    """Query AWS Bedrock and return a response."""
    bedrock = boto3.client("bedrock-runtime", region_name=AWS_BEDROCK_REGION)
    payload = {
        "messages": [{
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": prompt
            }]
        }
        ],
        "top_k": 250,
        "stop_sequences": [],
        "temperature": 1,
        "top_p": 0.999,
        "max_tokens": 4096,
        "anthropic_version": "bedrock-2023-05-31"
    }
    print (payload)
    response = bedrock.invoke_model(
        body=json.dumps(payload),
        modelId=AWS_BEDROCK_MODEL_ID,
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
    return json.dumps(response_body.get(["content"][0], "No response received."))

def save_responses(filename, username, ai_answers, user_answers):
    """Save AI-generated responses and user input to a CSV file."""
    file_exists = os.path.isfile(RESPONSES_FILE)
    with open(RESPONSES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header if the file is new
            writer.writerow(["Filename", "Username"] + 
                            [q["display_name"] + " (AI)" for q in QUESTIONS] + 
                            [q["display_name"] + " (User)" for q in QUESTIONS])
        # Write responses
        writer.writerow([filename, username] + list(ai_answers.values()) + list(user_answers.values()))

@app.route("/documents", methods=["GET"])
def list_documents():
    """List all documents."""
    files = [f for f in os.listdir(DOCUMENTS_DIR) if os.path.isfile(os.path.join(DOCUMENTS_DIR, f))]
    return jsonify(files)

@app.route("/documents/<filename>", methods=["GET"])
def get_document(filename):
    """Get the contents of a document."""
    filepath = os.path.join(DOCUMENTS_DIR, filename)
    if os.path.exists(filepath):
        return send_from_directory(DOCUMENTS_DIR, filename)
    return jsonify({"error": "File not found"}), 404

@app.route("/questions", methods=["GET"])
def get_questions():
    """Return the list of questions."""
    return jsonify(QUESTIONS)

@app.route("/analyze", methods=["POST"])
def analyze_document():
    """Analyze a document using Ollama and return answers."""
    data = request.json
    filename = data.get("filename")
    username = data.get("username")
    user_answers = data.get("user_answers", {})

    if not filename or not username:
        return jsonify({"error": "Filename and username are required"}), 400

    filepath = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    document_text = read_document(filepath)
    ai_answers = {}

    for question in QUESTIONS:
        prompt = f"Document: {document_text}\n\nQuestion: {question['prompt']}\nAnswer:"
        answer = query_aws_bedrock(prompt)
        ai_answers[question["display_name"]] = answer

        # Save AI-generated and user responses
        save_responses(filename, username, ai_answers, user_answers)

    return jsonify({"ai_answers": ai_answers})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
