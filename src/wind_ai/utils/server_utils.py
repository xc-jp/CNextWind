import os
import json
import random
from dotenv import load_dotenv, find_dotenv

import openai

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_json(prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0):
    """Function to get JSON text with intensity scores from OpenAI API


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
            )
        },
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


def get_completion(prompt: str, model="gpt-3.5-turbo"):
    """Function to get chat completion from OpenAI API.

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
    return response.choices[0].message["content"]


def random_values() -> str:
    """Fail safe function to generate random intensity values for words"""
    default_answer ={
        'Akihabara': {'intensity': random.random()},
        'district': {'intensity': random.random()},
        'Tokyo': {'intensity': random.random()},
        'Japan': {'intensity': random.random()},
        'electronics': {'intensity': random.random()},
        'shops': {'intensity': random.random()},
        'anime': {'intensity': random.random()},
        'manga': {'intensity': random.random()},
        'stores': {'intensity': random.random()},
        'video game': {'intensity': random.random()},
        'arcades': {'intensity': random.random()},
        'popular': {'intensity': random.random()},
        'destination': {'intensity': random.random()},
        'tourists': {'intensity': random.random()},
        'locals': {'intensity': random.random()},
        'interested': {'intensity': random.random()},
        'technology': {'intensity': random.random()},
        'gaming culture': {'intensity': random.random()}
    }

    return json.dumps(default_answer)

