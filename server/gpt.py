
# Importing necessary modules
import openai
from openai import OpenAI

# API key for accessing OpenAI services
api_key = "Your Api Key"

# Function to chat with OpenAI's GPT-3.5 model
def chat_with_openai(prompt, client, model_name="gpt-3.5-turbo"):
    # Constructing the message to send to the model
    message = {
        'role': 'user',  # Role of the message sender (in this case, user)
        'content': prompt  # Content of the message (prompt for the model)
    }

    # Sending the message to OpenAI's chat API and receiving the response
    response = client.chat.completions.create(
        model=model_name,  # Name of the model to use for completion
        messages=[message]  # Messages to send to the model
    )

    # Extracting the chatbot's response from the response object
    chatbot_response = response.choices[0].message.content
    
    return chatbot_response  # Returning the chatbot's response
