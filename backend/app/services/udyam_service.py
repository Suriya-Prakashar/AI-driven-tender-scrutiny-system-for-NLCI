import io
import logging
import os
import re
import time

import cv2
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.config import Config
from app.integrations.selenium.scrape import append_to_excel, scrape_page

logger = logging.getLogger(__name__)

UDYAM_PATTERN = re.compile(
    r"^[A-Za-z0-9]{5}\s?-\s?[A-Za-z]{2}\s?-\s?\d{2}\s?-\s?[A-Za-z0-9]{7}$"
)


def _configure_tesseract() -> None:
    if Config.TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH


def setup_chrome_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        if Config.CHROME_DRIVER_PATH:
            service = Service(Config.CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except WebDriverException as exc:
        logger.error("Failed to initialize Chrome WebDriver: %s", exc)
        raise


def preprocess_captcha_image(img_bytes: bytes) -> np.ndarray:
    pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    open_cv_image = np.array(pil_image)
    img = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return cv2.resize(cleaned, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)


def extract_captcha_text(processed_image: np.ndarray, max_retries: int = 3) -> str:
    _configure_tesseract()
    config = r"--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    for attempt in range(max_retries):
        try:
            captcha_text = pytesseract.image_to_string(processed_image, config=config).strip()
            captcha_text = re.sub(r"[^A-Z0-9]", "", captcha_text.upper())
            if captcha_text and len(captcha_text) >= 4:
                return captcha_text
            logger.warning("Attempt %s: invalid CAPTCHA text '%s'", attempt + 1, captcha_text)
        except Exception as exc:
            logger.error("OCR attempt %s failed: %s", attempt + 1, exc)

    return ""


def verify_udyam_number(
    udyam_number: str,
    max_captcha_attempts: int | None = None,
) -> tuple[bool, dict | None]:
    """Verify a single Udyam number via Selenium + OCR."""
    attempts = max_captcha_attempts or Config.MAX_CAPTCHA_ATTEMPTS
    driver = None
    scraped_data = None

    try:
        driver = setup_chrome_driver()
        driver.get(Config.UDYAM_PORTAL_URL)

        print_verify_xpath = "/html/body/form/header/div/div/div/nav/ul/li[4]/a"
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, print_verify_xpath))
        )
        ActionChains(driver).move_to_element(login_button).perform()

        udyam_verification_xpath = "/html/body/form/header/div/div/div/nav/ul/li[4]/ul/li[2]/a"
        verification_option = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, udyam_verification_xpath))
        )
        verification_option.click()
        time.sleep(5)

        captcha_img_xpath = "//*[@id='ctl00_ContentPlaceHolder1_imgCaptcha']"
        captcha_input_xpath = "//input[@id='ctl00_ContentPlaceHolder1_txtCaptcha']"
        submit_xpath = (
            "/html/body/form[1]/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div[2]/div[3]/div/input"
        )
        username_xpath = "//*[@id='ctl00_ContentPlaceHolder1_txtUdyamNo']"

        success = False
        for attempt in range(attempts):
            try:
                username_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, username_xpath))
                )
                username_field.clear()
                username_field.send_keys(udyam_number)

                captcha_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, captcha_img_xpath))
                )
                processed_image = preprocess_captcha_image(captcha_element.screenshot_as_png)
                captcha_text = extract_captcha_text(processed_image)

                if not captcha_text:
                    driver.refresh()
                    time.sleep(3)
                    continue

                captcha_input = driver.find_element(By.XPATH, captcha_input_xpath)
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                time.sleep(5)

                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, submit_xpath))
                )
                submit_button.click()
                time.sleep(8)

                current_url = driver.current_url.lower()
                if "printudyamapplication" in current_url or "home" in current_url:
                    success = True
                    break
                if "verify" not in current_url:
                    success = True
                    break

            except TimeoutException:
                if attempt < attempts - 1:
                    driver.refresh()
                    time.sleep(5)
            except Exception as exc:
                logger.error("Udyam attempt %s error: %s", attempt + 1, exc)
                if attempt < attempts - 1:
                    driver.refresh()
                    time.sleep(5)

        if success and driver:
            scraped_data = scrape_page(driver)
            append_to_excel(scraped_data, Config.UDYAM_OUTPUT_EXCEL)

        return success, scraped_data

    finally:
        if driver:
            driver.quit()


def get_udyam_numbers_from_excel(excel_path: str | None = None) -> list[str]:
    path = excel_path or Config.UDYAM_INPUT_EXCEL
    if not os.path.isfile(path):
        logger.warning("Udyam input Excel not found: %s", path)
        return []

    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower()
    column = Config.UDYAM_COLUMN.lower()

    if column not in df.columns:
        raise ValueError(f"Column '{Config.UDYAM_COLUMN}' not found in {path}")

    return df[column].dropna().astype(str).tolist()


def run_udyam_verification(excel_path: str | None = None) -> dict:
    """Run Udyam verification for all numbers in the input Excel."""
    numbers = get_udyam_numbers_from_excel(excel_path)
    results = []

    for entry in numbers:
        if not UDYAM_PATTERN.match(entry):
            results.append({"udyam_number": entry, "status": "invalid_format", "data": None})
            continue

        success, data = verify_udyam_number(entry)
        results.append(
            {
                "udyam_number": entry,
                "status": "verified" if success else "failed",
                "data": data,
            }
        )

    return {
        "processed": len(results),
        "results": results,
        "output_excel": Config.UDYAM_OUTPUT_EXCEL,
    }
