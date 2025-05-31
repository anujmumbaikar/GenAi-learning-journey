from google import genai

client = genai.Client(api_key="AIzaSyCnf3GeJo5_iAfrPtvGyJtmekBrhjR9hKo")

result = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents="dog chases cat",
)

print(result.embeddings)
print(len(result.embeddings[0].values))
