from openai import OpenAI
import os
import replicate
import re


# create environment for open ai
OPEN_AI_KEY = "create an openAI account and obtain an api key, then paste the key here"
client = OpenAI(
    api_key=OPEN_AI_KEY
)

# create the environment for Replicate
REPLICATE_TOKEN_KEY = "r8_IIZlatb6ZLMgaDsy6hx2gFIuBldfLMD4Xdhmo"
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN_KEY


def get_movie_recommendation_from_openai(prompt):
    """
        Get response from chatgpt based on the prompt given and returns the response
    :param prompt:
    :return:
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    new_data = []
    final_data = ""
    response = chat_completion.choices[0].message.content
    response = response.split('\n')
    response = response[2:]

    for data in response:
        if data == '':
            continue
        else:
            new_data.append(data)
    return new_data


def get_movie_recommendation_from_llama_replicate(prompt):
    output = replicate.run(
        "replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781",
        input={"prompt": prompt}
    )
    response = ""
    for item in output:
        # https://replicate.com/replicate/llama-2-70b-chat/versions/58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781/api#output-schema
        response += item

    movies = re.findall(r'"([^"]+)"', response)
    return movies


get_movie_recommendation_from_openai("Who are you")
