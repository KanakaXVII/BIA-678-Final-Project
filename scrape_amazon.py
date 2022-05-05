#/usr/bin/env python3
# Basic imports
import pandas as pd
import numpy as np
import re
import time
import csv
import warnings
import argparse
import os
import sys
from datetime import date, datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Set up help messages
help_msg_description = '''

'''

# Set a warning filter
warnings.filterwarnings('ignore')

# Set up the webdirver
def setup_driver():
    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--log-level=1')

    # Establish the Chromedriver service
    service = Service(ChromeDriverManager().install())

    # Create the driver and send it back
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Set up the scraper
def scrape(url, limit):
    # Set up storage
    new_df = pd.DataFrame()
    
    # Create the driver
    driver = setup_driver()

    while True:
        # Scroll to the bottom
        driver.execute_script('window,scrollTo(0,document.body.scrollHeight)')

        # Go to the page
        driver.get(url)

        # Get the list of reviews
        review_section = driver.find_element_by_css_selector('[id="cm_cr-review_list"]')
        review_list = review_section.find_elements_by_css_selector('[data-hook="review"]')
        

        # Iterate
        for review in review_list:
            if len(new_df) < limit:
                payload = {}

                # Look for review text
                try:
                    review_text = review.find_element_by_css_selector('[data-hook="review-body"]').text
                    payload['review'] = review_text
                except:
                    payload['review'] = None

                # Look for star value
                try:
                    # Get the star value of the review and extract the star value
                    stars_element = review.find_element_by_css_selector('[title*="out of 5 stars"]')
                    star_string = stars_element.get_attribute('title')
                    star_string_split = star_string.split(' ')
                    star = float(star_string_split[0])

                    # Create a binary label from stars
                    if star > 3:
                        payload['label'] = 1
                    else:
                        payload['label'] = 0
                
                except:
                    payload['label'] = None

                # add the payload to the dataframe
                new_df = new_df.append(payload, ignore_index=True)
            else:
                print('Limit reached.')
                driver.close()
                return new_df
        
        # Go to the next page
        try:
            next_button = WebDriverWait(driver,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'[class="a-last"]')))
            next_button.click()
            time.sleep(3)
        except Exception as e:
            print(e)


# Start the script
if __name__ == '__main__':
    # Build a parser
    parser = argparse.ArgumentParser(description=help_msg_description, formatter_class=argparse.RawTextHelpFormatter, add_help=False)
    parser.add_argument('URL', metavar='<url>', type=str, help='URL to Amazon review page.')
    parser.add_argument('--limit', metavar='<value>', type=int, help='Amount of results to scrape. Default is 100.')
    parser.add_argument('--output', metavar='<dir>', type=str, help='Output file location. If it is not specific, current directory is used.')
    args = parser.parse_args()

    # Check for optional limit parameters
    if args.limit is None:
        print('Note: Using default: 100')
        limit = 100
    else:
        print(f'Note: Using specified limit: {args.limit}')
        limit = args.limit
    
    # Perform scrape
    scrape_results = scrape(args.URL, limit)

    # Write results to file
    try:
        # Create a new file using the current date in the title 
        new_file = f'Amazon Scrape - {date.today()}'

        # Determine if there is a specific output directory
        if args.output is None:
            # Get the current path
            print('Generating file in current directory...')
            current_path = os.path.dirname(os.path.realpath(__file__))
            output_path = os.path.join(current_path, new_file)
        else:
            output_path = os.path.join(args.output, new_file)
            print(f'Generating file at: {output_path}')
        
        # Conver the dataframe to a file
        scrape_results.to_csv(f'{output_path}.csv', index=False)
        print(f'Created file "{new_file}"')

    except Exception as e:
        print(f'Something went wrong...{e}')
