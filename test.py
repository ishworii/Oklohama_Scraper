from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import string
import json
import requests
from contextlib import closing
from time import sleep
import os


# define some universal funtions for extraction
def xpath_finder(driver, xpath, many=False):
    if many:
        try:
            element = driver.find_elements(By.XPATH, xpath)
            return element
        except NoSuchElementException:
            return None
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element
    except NoSuchElementException:
        return None


def css_finder(driver, xpath, many=False):
    if many:
        try:
            element = driver.find_elements(By.CSS_SELECTOR, xpath)
            return element
        except NoSuchElementException:
            return None
    try:
        element = driver.find_element(By.CSS_SELECTOR, xpath)
        return element
    except NoSuchElementException:
        return None


def extract_list(driver):
    csv_link = xpath_finder(driver, "//a[contains(.,'.csv')]", many=True)
    if csv_link:
        return [x.get_attribute("href") for x in csv_link]


def extract_details(driver):

    # table name
    name = xpath_finder(driver, "//h1[@class='page-heading']")
    if not name:
        print("Table name not found...")
        return None
    name = name.text

    # table description
    table_description = xpath_finder(driver, "//div[@class='prose notes']")
    if not table_description:
        print("Table description not found...")
        # logging.info("table description not found.")
        return None
    table_description = table_description.text

    # table url
    table_url = driver.current_url

    # table download link
    actions_list = xpath_finder(driver, "//div[@class='actions']/ul/li", many=True)
    download_link = None
    for each_action in actions_list:
        if each_action.text == "Download":
            download_link = css_finder(each_action, "a").get_attribute("href")
            break
    if not download_link:
        print("Download link not found...")
        return None

    print(f"table name = {name}")
    print(f"description = {table_description}")
    print(f"url = {table_url}")
    print(f"download_table = {download_link}")


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)


driver.get("https://data.ok.gov/dataset/2022-real-property-asset-data")


sleep(2)

csv_links = extract_list(driver)
if not csv_links:
    print("CSV links not found...")
for each_link in csv_links:
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    # get the new url
    driver.get(each_link)
    sleep(5)
    extract_details(driver)
    # close and switch back to the original tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
