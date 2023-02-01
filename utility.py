from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import string
import json
import requests
from contextlib import closing
from time import sleep
import os
import logging
from typing import List

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
    csv_link = xpath_finder(driver, "//li[@class='resource-item']/a", many=True)
    if csv_link:
        return [x.get_attribute("href") for x in csv_link]


def extract_details(driver):

    # table name
    name = xpath_finder(driver, "//h1[@class='page-heading']")
    if not name:
        logging.info("Table name not found...")
        return None
    name = name.text

    # table description
    table_description = xpath_finder(driver, "//div[@class='prose notes']")
    if not table_description:
        logging.info("Table description not found...")
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
        logging.info("Download link not found...")
        return None

    # print(f"table name = {name}")
    # print(f"description = {table_description}")
    # print(f"url = {table_url}")
    # print(f"download_table = {download_link}")

    return name, table_description, table_url, download_link


# download csv file, and create all necessary metadata files
def save_everything(table_name, table_description, table_url, table_download):
    # convert table name to correct format
    table_name = table_name.split(".")[0]
    table_name = table_name.lower()
    table_name = table_name.encode("ascii", errors="ignore").decode()
    table_name = table_name.translate(str.maketrans("", "", string.punctuation))
    if len(table_name) > 80:
        table_name = table_name[:80]
    table_name = table_name.replace(" ", "_")

    if not os.path.isdir(table_name):
        os.mkdir(table_name)
    os.chdir(table_name)

    # download the csv file
    filename = f"{table_name}.csv"
    with closing(requests.get(table_download, stream=True)) as r:
        f = (line.decode("utf-8", errors="ignore") for line in r.iter_lines())
        with open(filename, "w", encoding="utf-8") as csvfile:
            for index, each_row in enumerate(f):
                if index == 300:
                    break
                csvfile.write(each_row)
                csvfile.write("\n")

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)
