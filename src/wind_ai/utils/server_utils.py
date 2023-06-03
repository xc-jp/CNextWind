import json
import os
import random
import socket

import openai
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_json(prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0) -> str:
    """Get JSON text with intensity scores from OpenAI API.

    Args:
        prompt: ANswer from ChatGPT to the user's prompt.
        model: OpenAI model to use.
        temperature: This is the degree of randomness of the model's output.
                     Should be between 0 and 1.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Generate a JSON text with intensity scores (float value from 0 to 1) corresponding to "
                "the amount of change the tokens in that word modify the embeddings of the sentence when "
                "replacing that word for its antonymous. your answer should only include Json and should be "
                "formatted like the following example:"
                '{\
                     "Love": {"intensity": 0.9},\
                     "intricate": {"intensity": 0.7},\
                     "tapestry": {"intensity": 0.5},\
                     "emotions": {"intensity": 0.8}\
                     }"'
            ),
        },
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]  # pyright: ignore[reportGeneralTypeIssues]


def get_completion(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Get chat completion from OpenAI API.

    Args:
        prompt: Original message from the user.
        model: OpenAI model to use.

    Returns:
        The model's answer.
    """
    messages = [{"role": "system", "content": "Answer using 50 words at most"}, {"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]  # pyright: ignore[reportGeneralTypeIssues]


def random_values() -> str:
    """Fail safe function to generate random intensity values for words."""
    default_answer = {
        "Akihabara": {"intensity": random.random()},
        "district": {"intensity": random.random()},
        "Tokyo": {"intensity": random.random()},
        "Japan": {"intensity": random.random()},
        "electronics": {"intensity": random.random()},
        "shops": {"intensity": random.random()},
        "anime": {"intensity": random.random()},
        "manga": {"intensity": random.random()},
        "stores": {"intensity": random.random()},
        "video game": {"intensity": random.random()},
        "arcades": {"intensity": random.random()},
        "popular": {"intensity": random.random()},
        "destination": {"intensity": random.random()},
        "tourists": {"intensity": random.random()},
        "locals": {"intensity": random.random()},
        "interested": {"intensity": random.random()},
        "technology": {"intensity": random.random()},
        "gaming culture": {"intensity": random.random()},
    }

    return json.dumps(default_answer)


def recv_end(listening_socket: socket.socket, end: str = "<EOF>", buffer_size: int = 4096) -> str:
    """Receive data from the given socket until the socket disconnects or the end message signal is received.

    Args:
        listening_socket: The socket to listen to.
        end: The end string that signals that the message has been received in its entirety.
        buffer_size: Buffer to use for the socket.

    Returns:
        The data received from the socket, as a utf-8 string.
    """
    end_bytes = end.encode()
    total_data: list[bytes] = []
    data = ""
    while True:
        data = listening_socket.recv(buffer_size)
        if not data:  # recv return empty message if client disconnects
            return data.decode("utf-8")
        if end_bytes in data:
            total_data.append(data[:data.find(end_bytes)])
            break
        total_data.append(data)
        if len(total_data) > 1:
            # check if end_of_data was split
            last_pair = total_data[-2] + total_data[-1]
            if end_bytes in last_pair:
                total_data[-2] = last_pair[:last_pair.find(end_bytes)]
                total_data.pop()
                break
    return b"".join(total_data).decode("utf-8")
