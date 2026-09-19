"""utils/skill_extractor.py"""
import re

KNOWN_SKILLS = [
    "python","java","javascript","typescript","react","angular","vue","node",
    "django","flask","fastapi","sql","postgresql","mysql","mongodb","redis",
    "aws","azure","gcp","docker","kubernetes","git","linux","machine learning",
    "deep learning","tensorflow","pytorch","pandas","numpy","rest api",
    "graphql","microservices","agile","html","css","c++","go","rust","kotlin",
    "swift","r","scala","spark","hadoop","tableau","power bi","excel","nlp"
]

def extract_skills(text: str) -> list:
    if not text:
        return []
    text_lower = text.lower()
    return [s for s in KNOWN_SKILLS if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]