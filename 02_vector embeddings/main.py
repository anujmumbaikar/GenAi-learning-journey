from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

client = genai.Client(api_key=api_key)

try:

    result = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents="dog chases cat",
    )

    # Validate the response
    if not result or not result.embeddings:
        raise ValueError("No embeddings returned from the API.")

    print(result.embeddings)
    print(len(result.embeddings[0].values))

except Exception as e:
    print(f"An error occurred: {e}")


chat_completion = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Write a short story about a dog chasing a cat.",
)
print(chat_completion.candidates[0].content.parts[0].text)
