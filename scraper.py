import os
from config import SEARCH_WORD
from bs4 import BeautifulSoup as bs
import requests
import re
import nltk
from nltk.corpus import stopwords
filtered_urls =[]
if filtered_urls == []:
    try:
        with open("filtered_urls.txt", "r", encoding="utf-8") as f:
            filtered_urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f'Error: {e}')
    

nltk.download("stopwords")
STOPWORDS = set(stopwords.words("english"))

SAVE_DIR = f"articles-{SEARCH_WORD}"
os.makedirs(SAVE_DIR, exist_ok=True)

def clean_text(text):
    text = re.sub(r"\s+", " ", text) 
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.lower().strip()

def extract_keywords(text, top_n=3):
    words = clean_text(text).split()
    freq = {}
    for w in words:
        if w not in STOPWORDS and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [w for w, _ in sorted_words[:top_n]]
    return "-".join(keywords) if keywords else "article"


for url in filtered_urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print('skip code not 200')
            continue

        soup = bs(response.text, "html.parser")
        content_div = soup.find("div", class_="block-region-middle")
        if not content_div:
            print("no content")
            continue

        paragraphs = content_div.find_all("p")
        text = "\n".join([p.get_text(strip=True) for p in paragraphs])

      
        filename = extract_keywords(text)
        file_path = os.path.join(SAVE_DIR, f"{filename}.txt")

    
        i = 1
        while os.path.exists(file_path):
            file_path = os.path.join(SAVE_DIR, f"{filename}_{i}.txt")
            i += 1

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved: {file_path}")

    except Exception as e:
        print(f"Error: {e}")