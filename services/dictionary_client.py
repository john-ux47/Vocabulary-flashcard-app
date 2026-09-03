import requests
from models.word import Word
from google import genai
import re

def clean_ai_text(text: str) -> str:
    if not text: return ""
    return re.sub(r"[\*\_#`]", "", text).strip()

class DictionaryClient:
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    def fetch_word_data(self, term: str) -> Word:
        try:
            url = f"{self.BASE_URL}/{term}"
            response = requests.get(url, timeout=20)
            if response.status_code == 404:
                raise ValueError(f"The word '{term}' was not found in the dictionary.")
            response.raise_for_status()
            
            data = response.json()[0]
            phonetic = data.get("phonetic", "")
            definitions, examples = [], []
            synonyms, antonyms = set(), set()

            for meaning in data.get("meanings", []):
                for syn in meaning.get("synonyms", []): synonyms.add(syn)
                for ant in meaning.get("antonyms", []): antonyms.add(ant)
                for d in meaning.get("definitions", []):
                    if d.get("definition"): definitions.append(d["definition"])
                    if d.get("example"): examples.append(d["example"])

            return Word(term=term, phonetic=phonetic, definitions=definitions[:4], 
                        examples=examples[:3], synonyms=list(synonyms)[:5], antonyms=list(antonyms)[:5])
        except Exception as e:
            raise ConnectionError(f"API Error: {str(e)}")

def enhance_word_with_gemini(word_obj: Word, api_key: str) -> Word:
    if not api_key: return word_obj
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"For '{word_obj.term}':\n1. Simple 1-sentence explanation.\n2. Example sentence.\n3. Memory trick.\nFormat: EXPLANATION: <text>\nEXAMPLE: <text>\nMEMORY_TRICK: <text>"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        for line in response.text.splitlines():
            if line.startswith("EXPLANATION:"): word_obj.simple_explanation = clean_ai_text(line.replace("EXPLANATION:", ""))
            elif line.startswith("EXAMPLE:"): word_obj.ai_example = clean_ai_text(line.replace("EXAMPLE:", ""))
            elif line.startswith("MEMORY_TRICK:"): word_obj.memory_trick = clean_ai_text(line.replace("MEMORY_TRICK:", ""))
    except Exception as e:
        print(f"Gemini enhancement failed: {e}")
    return word_obj