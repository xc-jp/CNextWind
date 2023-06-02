import argparse
import os
import openai
import json
import random
import socket
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.getenv('OPENAI_API_KEY')



def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, help="The prompt for the conversation")
    parser.add_argument("--socket", action="store_true", help="Receive prompt from socket")
    args = parser.parse_args()

    def get_completion(prompt, model="gpt-3.5-turbo"):
        # Function to get chat completion from OpenAI API
        messages = [{"role": "system", "content": "Answer using 50 words at most"},{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]

    def get_Json(prompt, model="gpt-3.5-turbo", temperature = 0):
        # Function to get JSON text with intensity scores from OpenAI API
        messages = [{"role": "system", "content": 'Generate a JSON text with intensity scores (float value from 0 to 1) corresponding to the amount of change the tokens in that word modify the embeddings of the sentence when replacing that word for its antonymous. \
        your answer should only include Json and should be formatted like the following example\
                     {\
              "Love": {"intensity": 0.9},\
              "intricate": {"intensity": 0.7},\
              "tapestry": {"intensity": 0.5},\
              "emotions": {"intensity": 0.8}\
                    }"'}, 
                    
                    {"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]


    if args.socket:
        prompt = receive_prompt_from_socket() # Receive prompt from socket
    else:
        prompt = args.prompt # Use prompt from command-line argument



    response = get_completion(prompt) # Get chat completion response from OpenAI
    words = get_Json(response) # Get JSON text with intensity scores

    def receive_prompt_from_socket():
        # Function to receive prompt from a socket connection
        HOST = 'localhost'  # Example host
        PORT = 12345  # Example port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)
            print(f"Listening on {HOST}:{PORT}...")

            conn, addr = s.accept()
            print(f"Connection established with {addr[0]}:{addr[1]}")

            data = conn.recv(1024).decode()
            conn.close()

            return data
                    
    print(response)
    #print(words)

    def random_values():
        # Fail safe function to generate random intensity values for words
        values = f'{{"Akihabara": {{"intensity": {random.random()}}},\
     "district": {{"intensity": {random.random()}}},\
     "Tokyo": {{"intensity": {random.random()}}},\
     "Japan": {{"intensity": {random.random()}}},\
     "electronics": {{"intensity": {random.random()}}},\
     "shops": {{"intensity": {random.random()}}},\
     "anime": {{"intensity": {random.random()}}},\
     "manga": {{"intensity": {random.random()}}},\
     "stores": {{"intensity": {random.random()}}},\
     "video game": {{"intensity": {random.random()}}},\
     "arcades": {{"intensity": {random.random()}}},\
     "popular": {{"intensity": {random.random()}}},\
     "destination": {{"intensity": {random.random()}}},\
     "tourists": {{"intensity": {random.random()}}},\
     "locals": {{"intensity": {random.random()}}},\
     "interested": {{"intensity": {random.random()}}},\
     "technology": {{"intensity": {random.random()}}},\
     "gaming culture": {{"intensity": {random.random()}}}}}'
        return json.loads(values)


    for i in range(2):
        try:
            output = json.loads(words) # Try to parse JSON response
            break

        except json.decoder.JSONDecodeError:
            words = get_Json(response, temperature = 0.5) # Retry with different temperature
        
        output = random_values() # Generate random intensity values if parsing fails


    print(output)

if __name__ == "__main__":
    main()