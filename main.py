from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import SEARCH_WORD,NUMBER_OF_LINKS
import time
import os
from bs4 import BeautifulSoup as bs
import requests
import re
import spacy


nlp = spacy.load("en_core_web_sm")
stopwords_list = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
]
nlp.Defaults.stop_words.update(stopwords_list)

#setup website for scraping
def collect_urls():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.finra.org")

    search_word = SEARCH_WORD
    wait = WebDriverWait(driver, 5)

    search_box = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "custom-landing-search"))
    )
    search_box.clear()
    search_box.send_keys(search_word + Keys.ENTER)


    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search-url")))



    allowed_sites = [
            "https://www.finra.org/media-center/news-releases/",
            "https://www.finra.org/investors/insights/",
            "https://www.finra.org/media-center/newsreleases",
            "https://www.finra.org/media-center/blog",
            "https://www.finra.org/media-center/",
    ]

    def is_allowed(url):
        return any(url.startswith(base) for base in allowed_sites)

    #search and save urls
    filtered_urls = [] 
    while len(filtered_urls) < NUMBER_OF_LINKS:
        result_links = driver.find_elements(By.CLASS_NAME, "search-url")
        urls = [link.text.strip() for link in result_links if link.text.strip()]
        new_urls = [u for u in urls if is_allowed(u) and u not in filtered_urls]
        filtered_urls.extend(new_urls)

        try:
            next_page_btn = driver.find_element(By.CLASS_NAME, "enabled")
            next_page_btn.click()
            time.sleep(2)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search-url")))
        except Exception:
            print("No next page found or can't click.")
            break
        
    print(f"Found {len(filtered_urls)} links:")
    for u in filtered_urls:
        print(u)
        
    #write all urls in filtered_urls.txt
    with open("filtered_urls.txt", "w", encoding="utf-8") as f:
        for url in filtered_urls:
            f.write(url + "\n")

    driver.quit()

#clean number and ignore space
def clean_text(text):
    text = re.sub(r"\s+", " ", text) 
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.lower().strip()

#scraping urls in filtered_urls.txt
def scrape_urls(filtered_urls, save_dir):
    for url in filtered_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print('status code not 200')
                continue

            soup = bs(response.text, "html.parser")
            content_div = soup.find("div", class_="block-region-middle")
            if not content_div:
                print(f"No content")
                continue

            paragraphs = content_div.find_all("p")
            text = "\n".join([p.get_text(strip=True) for p in paragraphs])
            text = clean_text(text)
            
            doc = nlp(text)
            cleaned_text = " ".join(
                [token.text for token in doc if token.is_alpha and not token.is_stop]
            )
            
            filename = (
                url.replace("https://", "")
                   .replace("http://", "")
                   .replace("/", "-")
                   .replace("?", "-")
                   .replace("=", "-")
                   .replace("&", "-")
                   .replace("%", "-")
            )
            # Keep only safe filename characters
            filename = re.sub(r"[^a-zA-Z0-9\-.]", "-", filename)
            file_path = os.path.join(save_dir, f"{filename}.txt")

            # Write (replace if exists)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            print(f"Saved (replaced if existed): {file_path}")

        except Exception as e:
            print(f"Error {url}: {e}")
    
def main():
    collect_urls()

    SAVE_DIR = f"articles-{SEARCH_WORD}"
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    filtered_urls =[]
    if filtered_urls == []:
        try:
            with open("filtered_urls.txt", "r", encoding="utf-8") as f:
                filtered_urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f'Error: {e}')
            
    scrape_urls(filtered_urls,SAVE_DIR)
    
        
    
if __name__ == "__main__":
    main()
