import requests
import json
import os
from milvus import default_server
from server.util import print_centered_text, print_title, strip_non_alpha, parse_command

# URL of the server
url = 'http://127.0.0.1:5000'

# Function to parse the response data
def get_response_data(response):
    if isinstance(response, dict):
        return response
    try:
        response_json = dict(json.loads(response.content.decode('utf-8')))
        return response_json
    except:
        return response

# Function to load the application
def load_app(clear_db=True):
    response = requests.request("GET", url + "/load_app", json={"clear_db": clear_db})
    if response.status_code == 200:
        return "Loaded successfully!"
    return "Not loaded! Please restart the server (disable and restart app.py and client.py))"

# Function to add a document
def add_document(file_path):
    try:
        response = requests.post(url + "/add_document", json={'file': "../" + file_path})
        if response.status_code == 200:
            return f"\"{file_path}\" inserted successfully"
        else:
            return f"{file_path} not inserted!"
    except Exception as e:
        return str(e)

# Function to ask a question
def ask_question(prompt):
    try:
        response = requests.post(url + "/ask_question", json={'prompt': prompt})
        output = get_response_data(response)
        if isinstance(output, dict):
            result = {
                "status": "success",
                "output": {"output_text": output["output_text"], "prompt": output["prompt"]} 
            } 
            return result
        return {
            "status": "faild",
            "output": output
        }
    except Exception as e:
        return {
            "status": "faild",
            "output": str(e)
            }

# Printing server starting message
print_centered_text("Server starting!")
command = "start"

# Starting the server
with default_server:
    print_centered_text("Server started!")
    # Running the command loop
    while not command == "end":
        command = input(
            "________________________________________________________________________________________________"
            "\nEnter the command:\n"
            "\t\t- 'load' or 'load empty'\n"
            "\t\t\t\t\t'load': for setup database'\n\t\t\t\t\t'load empty': for to empty and setup database.\n"
            "\t\t- 'add folderPath' (e.g., add foldername)\n"
            "\t\t\t\t\t'folderPath is the folder that contains the files you want to import into the database․\n"
            "\t\t- 'ask question' (e.g., 'ask Что необходимо проверить при сверке по счетам 62.02 и 76.АВ?')\n"
            "\t\t\t\t\t 'question: your question\n"
            "\t\t- 'end: for quit'\n"
            "________________________________________________________________________________________________\n"
            ": "
        ).lower()

        # Parsing the command
        action, parameters = parse_command(command)
        
        if action == "load":
            if not (parameters is None or parameters == "empty"):
                print_centered_text("Uncorrect command")
            else:
                clear_db = parameters == "empty"
                load_status = load_app(clear_db=clear_db)
                print_centered_text(load_status)

        elif action == "add":
            if parameters:
                folder_path = parameters
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        if os.path.isfile(os.path.join(folder_path, filename)):
                            file_path = os.path.join(folder_path, filename)
                            add_status = add_document(file_path)
                            print_centered_text(add_status)
                else:
                    print_centered_text("Uncorrect folder path1")                                
            else:
                print_centered_text("Uncorrect folder path2")
                
        elif action == "ask":
            if parameters:
                question = parameters
                response = ask_question(question)
                if response["status"] == "faild":
                    print_centered_text(response["output"])
                else:
                    output = get_response_data(response["output"])
                    if isinstance(output, dict):
                        print_title("Response")
                        print(strip_non_alpha(output["output_text"]), end="\n\n")
                    else:
                        print(output, end="\n\n")
            else:
                print_centered_text("Uncorrect question")
        elif action == "end":
            print("_"*40)
            break
        else:
            print_centered_text("Uncorrect command:")                    
