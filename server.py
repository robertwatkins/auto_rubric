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
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # Change to your installed Ollama model

# Load questions from JSON
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

def read_document(filepath):
    """Read a document's contents."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def query_ollama(prompt):
    """Query Ollama locally and return a response."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response", "No response received.") if response.status_code == 200 else "Error"

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
        answer = query_ollama(prompt)
        ai_answers[question["display_name"]] = answer

    # Save AI-generated and user responses
    save_responses(filename, username, ai_answers, user_answers)

    return jsonify({"ai_answers": ai_answers})

if __name__ == "__main__":
    app.run(debug=True, port=5000)