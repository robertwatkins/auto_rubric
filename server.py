from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import requests

app = Flask(__name__)
CORS(app)  # Allow frontend requests

DOCUMENTS_DIR = "./documents"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # Change to your local Ollama model

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
    
    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    filepath = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    document_text = read_document(filepath)
    answers = {}

    for question in QUESTIONS:
        prompt = f"Document: {document_text}\n\nQuestion: {question['prompt']}\nAnswer:"
        answer = query_ollama(prompt)
        answers[question["display_name"]] = answer

    return jsonify(answers)

if __name__ == "__main__":
    app.run(debug=True, port=5000)