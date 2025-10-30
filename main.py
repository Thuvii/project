from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import SEARCH_WORD
import time
import os
from bs4 import BeautifulSoup as bs
import requests
import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
STOPWORDS = set(stopwords.words("english"))

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
    while len(filtered_urls) < 10:
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


def extract_keywords(text, top_n=3):
    words = clean_text(text).split()
    freq = {}
    for w in words:
        if w not in STOPWORDS and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [w for w, _ in sorted_words[:top_n]]
    return "-".join(keywords) if keywords else "article"

#scraping urls in filtered_urls.txt
def scrape_urls(filtered_urls,save_dir):
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
            file_path = os.path.join(save_dir, f"{filename}.txt")

        
            i = 1
            while os.path.exists(file_path):
                file_path = os.path.join(save_dir, f"{filename}_{i}.txt")
                i += 1

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"Saved: {file_path}")

        except Exception as e:
            print(f"Error: {e}")
    
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
