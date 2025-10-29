from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import SEARCH_WORD
import time

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
with open("filtered_urls.txt", "w", encoding="utf-8") as f:
    for url in filtered_urls:
        f.write(url + "\n")

driver.quit()
