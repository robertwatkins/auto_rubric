from datetime import datetime
import os
import requests
import json
import csv

# Configurations
OLLAMA_URL = "http://localhost:11434/api/generate"  # Adjust if necessary
MODEL = "llama3.2"  # Change this to your installed Ollama model
DOCUMENTS_DIR = "./documents"  # Folder where documents are stored
QUESTIONS = [
    "What is the main topic of this document?",
    "Are there instructions for setup and configuration? Answer with just 'Yes' or 'No'.",
    "Are the configuration options explained? Answer with just 'Yes' or 'No'.",
    "Are there usage examples provided? Answer with just 'Yes' or 'No'.",
    "Are the prerequisites for using this document mentioned? Answer with just 'Yes' or 'No'.",
    "Are tests included? Answer with just 'Yes' or 'No'.",
    "Is there information about how to run the tests? Answer with just 'Yes' or 'No'.",
    "Does this document mention any risks or challenges?",
]

def read_document(filepath):
    """Read the contents of a text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def query_ollama(prompt):
    """Send a query to the local Ollama API and return the response."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False  # Change to True if you want to stream responses
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "No response received.")
    else:
        return f"Error: {response.status_code} - {response.text}"

def process_documents():
    """Loop through documents, ask questions, and generate a report."""
    report_data = []

    for filename in os.listdir(DOCUMENTS_DIR):
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        document_text = read_document(filepath)
        doc_results = {"Filename": filename}

        for question in QUESTIONS:
            prompt = f"Document: {document_text}\n\nQuestion: {question}\nAnswer:"
            answer = query_ollama(prompt)
            doc_results[question] = answer

        report_data.append(doc_results)

    return report_data

def save_report(report_data, output_file="report.csv"):
    """Save the results to a CSV file."""
    if not report_data:
        print("No data to save.")
        return

    fieldnames = ["Filename"] + QUESTIONS
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)

    print(f"Report saved to {output_file}")

if __name__ == "__main__":
    print(datetime.now().strftime("%H:%M:%S"))
    report = process_documents()
    save_report(report)
    print(datetime.now().strftime("%H:%M:%S"))