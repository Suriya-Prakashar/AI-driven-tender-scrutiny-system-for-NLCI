"""
===============================================================
Udyam number and Company Verification through captcha bypassing
===============================================================

This is a Python program that Gets through the udyam verification with udyam number and captcha bypass automatically
and then stores the required fields from the verified webpage of the company to a excel sheet.

Installation:
In VS studio code terminal run the following commands:
venv\Scripts\activate
pip install -r requirements.txt

Install the tesseract.exe application given in the Folder and add it to the system path.
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image
import io
import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
from Scrape_and_excel import scrape_page
from Scrape_and_excel import append_to_excel

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

file_path = r"C:/Users/syles/Documents/NLC/N8N.xlsx"  # <-- Change this to your Excel path
udyam_column = "udyam registration" #coloumn name in the excel sheet

def setup_chrome_driver():
    """
    Set up Chrome WebDriver with proper configuration
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    # Configure Chrome options for better performance and reliability
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start browser maximized
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-extensions")  # Disable extensions for faster loading
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    
    try:
        # Use ChromeDriverManager to automatically manage ChromeDriver
        # If you prefer manual path, uncomment and modify the line below:
        # service = Service(r'C:\chromedriver.exe')
        
        # For automatic driver management, install webdriver-manager:
        # pip install webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        
        # For now, using system PATH (make sure chromedriver is in PATH)
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    
    except WebDriverException as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        raise

def preprocess_captcha_image(img_bytes):
    """
    Preprocess CAPTCHA image for better OCR accuracy
    
    Args:
        img_bytes (bytes): Raw image bytes from screenshot
        
    Returns:
        numpy.ndarray: Preprocessed image ready for OCR
    """
    try:
        # Convert bytes to PIL Image and then to OpenCV format
        pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        open_cv_image = np.array(pil_image)
        img = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale for better processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to create binary image (black text on white background)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Create morphological kernel for noise reduction
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        
        # Apply morphological operations to clean the image
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Resize image to improve OCR accuracy (3x scaling)
        resized = cv2.resize(cleaned, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # Optional: Save processed image for debugging
        #cv2.imwrite("captcha_processed.png", resized)
        logger.info("CAPTCHA image preprocessed successfully")
        
        return resized
    
    except Exception as e:
        logger.error(f"Error preprocessing CAPTCHA image: {e}")
        raise

def extract_captcha_text(processed_image, max_retries=3):
    """
    Extract text from preprocessed CAPTCHA image using OCR
    
    Args:
        processed_image (numpy.ndarray): Preprocessed CAPTCHA image
        max_retries (int): Maximum number of OCR attempts
        
    Returns:
        str: Extracted CAPTCHA text
    """
    for attempt in range(max_retries):
        try:
            # Configure Tesseract for alphanumeric characters only
            config = r'--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Extract text using OCR
            captcha_text = pytesseract.image_to_string(processed_image, config=config).strip()
            
            # Clean the extracted text (remove spaces and special characters)
            captcha_text = re.sub(r'[^A-Z0-9]', '', captcha_text.upper())
            
            if captcha_text and len(captcha_text) >= 4:  # Assuming minimum 4 character CAPTCHA
                logger.info(f"CAPTCHA text extracted successfully: {captcha_text}")
                return captcha_text
            else:
                logger.warning(f"Attempt {attempt + 1}: Invalid CAPTCHA text: '{captcha_text}'")
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}: OCR error: {e}")
    
    logger.error("Failed to extract valid CAPTCHA text after all attempts")
    return ""

def login_to_gem_portal(username, max_captcha_attempts=5):
    """
    Main function to automate GeM portal login
    
    Args:
        username (str): Login username
        max_captcha_attempts (int): Maximum CAPTCHA solving attempts
        
    Returns:
        bool: True if login successful, False otherwise
    """
    driver = None
    
    try:
        # Initialize Chrome WebDriver
        driver = setup_chrome_driver()
        
        # Navigate to GeM portal
        logger.info("Navigating to Udyam Verification portal...")
        driver.get("https://udyamregistration.gov.in/Government-India/Ministry-MSME-registration.htm")
        
        # Wait for page to load and click Login button
        logger.info("Hovering over on print/verify tab...")
        print_verify_xpath = "/html/body/form/header/div/div/div/nav/ul/li[4]/a"
        
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, print_verify_xpath))
        )
        ActionChains(driver).move_to_element(login_button).perform()

        logger.info("Clicking Udyam Verification portal option...")
        udyam_verification_xpath = "/html/body/form/header/div/div/div/nav/ul/li[4]/ul/li[2]/a"
    
        verification_option = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, udyam_verification_xpath))
        )
        verification_option.click()
        
        # Wait for login form to appear
        time.sleep(5)
        
        # Define CAPTCHA element XPaths
        captcha_img_xpath = "//*[@id='ctl00_ContentPlaceHolder1_imgCaptcha']"
        captcha_input_xpath = "//input[@id='ctl00_ContentPlaceHolder1_txtCaptcha']"
        submit_xpath = "/html/body/form[1]/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div[2]/div[3]/div/input"
        
        # Attempt CAPTCHA solving with retries
        for attempt in range(max_captcha_attempts):
            try:

                # Enter username
                logger.info(f"Entering username: {username}")
                username_xpath = "//*[@id='ctl00_ContentPlaceHolder1_txtUdyamNo']"
        
                # The below has been copies into the loop
                username_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, username_xpath))
                )
                username_field.clear()
                username_field.send_keys(username)

                logger.info(f"CAPTCHA attempt {attempt + 1}/{max_captcha_attempts}")
                
                # Wait for CAPTCHA image to load
                captcha_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, captcha_img_xpath))
                )
                
                # Take screenshot of CAPTCHA
                img_bytes = captcha_element.screenshot_as_png
                
                # Process CAPTCHA image
                processed_image = preprocess_captcha_image(img_bytes)
                
                # Extract CAPTCHA text using OCR
                captcha_text = extract_captcha_text(processed_image)
                
                if not captcha_text:
                    logger.warning("No valid CAPTCHA text extracted, refreshing...")
                    driver.refresh()
                    time.sleep(3)
                    continue
                
                # Enter CAPTCHA value
                captcha_input = driver.find_element(By.XPATH, captcha_input_xpath)
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                
                logger.info(f"Entered CAPTCHA: {captcha_text}")
                
                # Add small delay before submission
                time.sleep(5)
                
                # Submit the login form
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, submit_xpath))
                )
                submit_button.click()
                
                # Wait to check if login was successful
                time.sleep(8)
                
                # Check for successful login (you may need to adjust this based on actual response)
                current_url = driver.current_url
                if "printudyamapplication" in current_url.lower() or "home" in current_url.lower():
                    logger.info("Login successful!")
                    return True
                elif "verify" in current_url.lower():
                    logger.warning("Login failed, likely incorrect CAPTCHA. Retrying...")
                    # Clear the CAPTCHA field for next attempt
                    try:
                        captcha_input.clear()
                    except:
                        pass
                else:
                    logger.info("Login status unclear, please check manually")
                    logger.info(f"{current_url}")
                    time.sleep(10)  # Give time to manually verify
                    return True
                    
            except TimeoutException:
                logger.error(f"Timeout on attempt {attempt + 1}")
                if attempt < max_captcha_attempts - 1:
                    driver.refresh()
                    time.sleep(5)
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_captcha_attempts - 1:
                    driver.refresh()
                    time.sleep(5)
        
        logger.error("All CAPTCHA attempts failed")
        return False
        
    except Exception as e:
        logger.error(f"Critical error during login process: {e}")
        # Save screenshot for debugging
        if driver:
            try:
                driver.save_screenshot("error_screenshot.png")
                logger.info("Error screenshot saved as 'error_screenshot.png'")
            except:
                pass
        return False
        
    finally:
        # Close browser
        if driver:
            scraped = scrape_page(driver)
            print(scraped)
            append_to_excel(scraped)
            EXCEL_PATH = r"C:/Users/syles/Documents/NLC/scraped_output.xlsx"
            print(f"Data appended to {EXCEL_PATH}")
            time.sleep(20)
            logger.info("Closing browser...")
            time.sleep(10)  # Brief pause before closing
            driver.quit()

def get_udyam_numbers(file_path):
    try:

        if os.path.isfile(file_path):
            print("✅ File exists")
        else:
            print("❌ File not found")

        # Read the Excel file
        df = pd.read_excel(file_path)
        print("Reading file in given file path")

        # Normalize column names (strip spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower()

        # Find the "udyam registration number" column
        if udyam_column in df.columns:
            udyam_list = df["udyam registration"].dropna().astype(str).tolist()
            return udyam_list
        else:
            raise ValueError("Column 'Udyam registration' not found in the file.")
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    """
    Main execution function
    """
    udyam_numbers=[]
    udyam_numbers = get_udyam_numbers(file_path)

    # udyam_numbers=["UDYAM-MH-19-0172588"]

    print("Extracted Udyam Numbers:")
    print(udyam_numbers)

    # Configuration
    # Replace with your actual username

    success = None

    for entry in udyam_numbers:

        MAX_CAPTCHA_ATTEMPTS = 50  # Adjust based on your needs

        # Regex pattern for both formats
        pattern = r"^[A-Za-z0-9]{5}\s?-\s?[A-Za-z]{2}\s?-\s?\d{2}\s?-\s?[A-Za-z0-9]{7}$"

        if re.match(pattern, entry):
            print("✅ String matches the required format")
            # You can put your processing code here

            # Attempt login
            success = login_to_gem_portal(entry, MAX_CAPTCHA_ATTEMPTS)

        else:
            print("❌ String does not match the required format")


        logger.info("Starting GeM Portal automation...")
        logger.info(f"attempting {entry}")
    
    if success:
        logger.info("Automation completed successfully!")
    else:
        logger.error("Automation failed. Please check the logs and try again.")

if __name__ == "__main__":
    main()
