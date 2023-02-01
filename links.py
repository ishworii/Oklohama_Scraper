from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging
import sys
import pandas as pd
import json


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

driver.get("https://data.ok.gov/dataset?res_format=CSV&page=1")

sleep(4)

arr = []


while True:
    all_divs = driver.find_elements(By.XPATH, "//li[@class='dataset-item']")
    print(f"Found {len(all_divs)} links in the page..")
    for each_div in all_divs:
        link = each_div.find_element(
            By.CSS_SELECTOR, "h3.dataset-heading a"
        ).get_attribute("href")
        tmp = {"link": link, "scraped": False}
        arr.append(tmp)

    pagination = driver.find_elements(
        By.XPATH, "//div[@class='pagination pagination-centered']/ul/li"
    )
    next_button = None
    for each_button in pagination:
        if each_button.text == "»":
            next_button = each_button.find_element(By.CSS_SELECTOR, "a")
            break

    if not next_button:
        print("END...")
        break

    driver.get(next_button.get_attribute("href"))


df = pd.DataFrame(arr)
df.to_json("links_oklohama.json", orient="records")
