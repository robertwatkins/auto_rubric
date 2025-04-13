# Auto-Rubric
## Overview
This is an experimental tool to auto-generate an evaluation of a README file to determine if it meets some basic requirements for a 'good' README.

## Approach
The approach is to use an isolated LLM to perform this work. For this epxeriement, I've chosen Ollama and llama3.2.

I've pulled random README files from public repositories on github.

# Limitations
It would be trivial to fool this system into thinking the README was actually 'good'. As a supporting mechanism to a review process, it is probably useful.

## Rubric
TBD

## Setup

Install Ollama
Install Python3

```
pip install requests

## How to run
python3 auto_rubric.py
```
## Reading the output
There is a 'report.csv' file generated that shows the results

## Troubleshooting
```
ollama list
```

make sure you have llama3.2 installed or update the model specified to match the model you're using

# TODO
 - put questions in a file to make it more flexible
 - Generate a formatted result to make the results more readable
 - Generate a score, based on yes/no answers
 - Validate the work by adding in a way for folks to produce their own results and compared to calucated results
 - Update the model (or instructions) to account for these differences
 - Build a manual review process around reviewing READMEs to provide a 'complete' picture of the evaluation of this document.


# Server
## Prerequisites
pip install flask flask-cors requests


python server.py