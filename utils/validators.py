import re

def validate_word(word: str) -> tuple[bool, str]:
    if not word or not word.strip():
        return False, "Input cannot be empty."
    
    cleaned = word.strip().lower()
    if not re.fullmatch(r"^[a-zA-Z]+(-[a-zA-Z]+)?$", cleaned):
        return False, "Please enter a valid single word (letters only)."
        
    return True, cleaned
