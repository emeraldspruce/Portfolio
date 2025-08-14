# app/content_loader.py
import json
import pathlib

CONTENT_DIR = pathlib.Path(__file__).parent.parent / "content"

def load_json(filename: str):
    path = CONTENT_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
