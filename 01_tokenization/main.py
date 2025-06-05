import tiktoken

enc = tiktoken.encoding_for_model('gpt-4o');
text = "Hello, I Live in Mumbai";
tokens = enc.encode(text)
print(tokens)

tokens_decoded = enc.decode([13225, 11, 357, 939, 1689, 5848, 391, 31084, 50449])
print(tokens_decoded)
