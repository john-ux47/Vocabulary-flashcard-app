from dotenv import load_dotenv
import os
from services.dictionary_client import DictionaryClient, enhance_word_with_gemini

load_dotenv()

client = DictionaryClient()
word = client.fetch_word_data("happy")

print("Term:", word.term)
print("Phonetic:", word.phonetic)
print("Definitions:", word.definitions)
print("Examples:", word.examples)
print("Synonyms:", word.synonyms)
print("Antonyms:", word.antonyms)

api_key = os.getenv("GEMINI_API_KEY")
word = enhance_word_with_gemini(word, api_key)

print("Simple explanation:", word.simple_explanation)
print("AI example:", word.ai_example)
print("Memory trick:", word.memory_trick)
