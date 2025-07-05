from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import os

# Load environment variables with keys
load_dotenv()
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
GEMINI_AI_KEY = os.getenv("GEMINI_AI_KEY")

# Initialize OpenAI and Google Gemini client objects
client = OpenAI(api_key=OPEN_AI_KEY)
client_gem = genai.Client(api_key=GEMINI_AI_KEY)


# def get_movie_recommendation_from_openai(prompt):
#     """
#     Get response from ChatGPT based on the prompt given and returns the response
#     :param prompt: User input prompt (str)
#     :return: List of non-empty response lines
#     """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4.1",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],
#         )
#
#         # Extract content from response
#         content = response.choices[0].message.content
#         # Split by newlines and clean up
#         new_data = []
#
#         content = content.split("\n")
#
#         for data in content:
#             if data == "":
#                 continue
#             else:
#                 new_data.append(data)
#
#         return new_data
#
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return []



#  Using the GOOGLE GEMINI API

def get_movie_recommendation_from_gemini(prompt):
    response = client_gem.models.generate_content(
        model="gemini-2.0-flash", contents= prompt
    )
    new_data = []

    content = response.text.split("\n")

    for data in content:
        if data == "":
            continue
        else:
            new_data.append(data)
    return new_data
