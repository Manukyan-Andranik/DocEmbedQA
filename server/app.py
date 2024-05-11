from flask import Flask, jsonify, request
from database import DataBase
from text_splitter import TextSplitter
from gpt import chat_with_openai
from openai import OpenAI

app = Flask(__name__)

# API key for OpenAI
api_key = "Your Api Key"

# Initialize instances of necessary classes
splitter = TextSplitter()
database = DataBase(spliter=splitter, api_key=api_key)


# Route to load the app and setup the database
@app.route('/load_app', methods=['GET'])
def load_app():
    # Check if 'clear_db' flag is present in the request
    if "clear_db" in request.json:
        clear_db = request.json["clear_db"]
        
    # Setup the database, optionally clearing it if 'clear_db' is True
    database.setup(clear_db=clear_db)
    return jsonify({'message': 'App loaded successfully'}), 200


# Route to add a document to the database
@app.route('/add_document', methods=['POST'])
def add_document():
    # Check if 'file' key is present in the request
    if "file" not in request.json:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.json["file"]
    
    # Check if the file is empty
    if file == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Load the document into the database
    status = database.load_document(file)
    
    if status:
        return jsonify({'message': 'Document added successfully'}), 200
    
    return jsonify({'error': 'Failed to read file'}), 400


# Route to ask a question based on a prompt
@app.route('/ask_question', methods=['POST'])
def ask_question():
    # Check if 'prompt' key is present in the request
    if 'prompt' not in request.json:
        return jsonify({'error': 'No input text provided'}), 400
    
    text = request.json['prompt']
    
    # Search the database for relevant information based on the input text
    prompt = database.search(text)
    
    # Format the prompt for OpenAI chat
    prompt = "Summarize in russian\n" + prompt.replace("\n", " ")
    
    # Get the response from OpenAI based on the modified prompt
    output_text = chat_with_openai(prompt,  client=OpenAI(api_key=api_key))
    
    return jsonify({'output_text': output_text, 'prompt': prompt}), 200


if __name__ == '__main__':
    app.run(debug=True)
