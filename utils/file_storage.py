import json
import os

def load_json(filepath: str, default_val=None):
    if default_val is None: 
        default_val = []
    if not os.path.exists(filepath): 
        return default_val
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except: 
        return default_val

def save_json(filepath: str, data) -> bool:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except: 
        return False
    