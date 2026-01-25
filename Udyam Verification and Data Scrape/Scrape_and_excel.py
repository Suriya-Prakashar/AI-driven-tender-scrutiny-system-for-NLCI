import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Path for storing scraped results
EXCEL_PATH = r"C:/Users/syles/Documents/NLC/scraped_output.xlsx"

def safe_find_text(driver, by, locator) -> str:
    """Return text of element, or empty string if not found."""
    try:
        el = driver.find_element(by, locator)
        return el.text.strip()
    except NoSuchElementException:
        return ""
    
LOCATORS = {
    "Name of the Enterprise": (By.ID, "ctl00_ContentPlaceHolder1_lblEnterpriseName"),
    "Udyam Registration number": (By.ID, "ctl00_ContentPlaceHolder1_lbludyamregNo"),
    "Major Activity": (By.ID, "ctl00_ContentPlaceHolder1_lblServices"),
    "Classification Year 1": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[2]/td[3]"),
    "Enterprise Type 1": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[2]/td[4]"),
    "Classification Year 2": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[3]/td[3]"),
    "Enterprise Type 2": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[3]/td[4]"),
    "Classification Year 3": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[4]/td[3]"),
    "Enterprise Type 3": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[4]/td[4]"),
    "Classification Year 4": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[5]/td[3]"),
    "Enterprise Type 4": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[3]/tbody/tr[5]/td[4]"),
    "Nic 2 Digit [1]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[2]/td[2]"),
    "Nic 4 Digit [1]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[2]/td[3]"),
    "Nic 6 Digit [1]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[2]/td[4]"),
    "Activity [1]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[2]/td[5]"),
    "Date [1]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[2]/td[6]"),
    "Nic 2 Digit [2]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[3]/td[2]"),
    "Nic 4 Digit [2]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[3]/td[3]"),
    "Nic 6 Digit [2]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[3]/td[4]"),
    "Activity [2]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[3]/td[5]"),
    "Date [2]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[3]/td[6]"),
    "Nic 2 Digit [3]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[4]/td[2]"),
    "Nic 4 Digit [3]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[4]/td[3]"),
    "Nic 6 Digit [3]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[4]/td[4]"),
    "Activity [3]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[4]/td[5]"),
    "Date [3]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[4]/td[6]"),
    "Nic 2 Digit [4]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[5]/td[2]"),
    "Nic 4 Digit [4]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[5]/td[3]"),
    "Nic 6 Digit [4]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[5]/td[4]"),
    "Activity [4]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[5]/td[5]"),
    "Date [4]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[5]/td[6]"),
    "Nic 2 Digit [5]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[6]/td[2]"),
    "Nic 4 Digit [5]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[6]/td[3]"),
    "Nic 6 Digit [5]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[6]/td[4]"),
    "Activity [5]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[6]/td[5]"),
    "Date [5]": (By.XPATH, "/html/body/form/div[3]/div/div[2]/div/div/div/div/div[2]/div/div/div/div/table/tbody/tr/td/table[6]/tbody/tr[6]/td[6]")
}

def scrape_page(driver):
    """Scrape all required fields into a dict."""
    result = {}
    for field, (by, loc) in LOCATORS.items():
        result[field] = safe_find_text(driver, by, loc)
    return result

def append_to_excel(data: dict, excel_path: str = EXCEL_PATH):
    """Append scraped data into Excel, create if missing."""
    df_new = pd.DataFrame([data])
    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path, engine="openpyxl")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(excel_path, index=False, engine="openpyxl")
    else:
        df_new.to_excel(excel_path, index=False, engine="openpyxl")

# ---------------- Example usage ----------------
# After login and navigation:
# scraped = scrape_page(driver)
# print(scraped)
# append_to_excel(scraped)
# print(f"Data appended to {EXCEL_PATH}")
