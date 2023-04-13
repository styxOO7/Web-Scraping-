
# --------------------------------------------- DEPENDENCIES -------------------------------------------------------


import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

import requests
import urllib.request
from pytesseract import image_to_string 
from PIL import Image
import pytesseract

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import os
import sys
import pickle
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException




# --------------------------------------------- FUNCTIONS -------------------------------------------------------

# function to get captcha text from image:
pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR/tesseract'
def decode():
    im = Image.open('image.png') 

    captcha_text = image_to_string(im)
    captcha_text = captcha_text.replace(" ", "")
    
    os.remove('image.png')
    return captcha_text

# load saved list of all given localities:
with open('my_list.pkl', 'rb') as f:
    all_localities = pickle.load(f)

# function to extract data from current page:
def get_data(data):
    # Extract the table elements:
    regno_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[1]/span')
    reg_date_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[2]/span')

    first_party_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[3]/span')
    second_party_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[4]/span')

    property_address_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[5]/span')
    area_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[6]/span')

    deed_type_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[7]/span')
    property_type_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[8]/span')


    # Store the table data after data cleaning (converting to proper units):
    for i in range(0, 9):
        area_text = area_data[i].text
        if "Sq. Meter" in area_text:
            area = float(area_text.split()[0]) * 10.7639
        elif "Sq. Yard" in area_text:
            area = float(area_text.split()[0]) * 9
        else:
            area = float(area_text.split()[0])
        tmp = {
            'Reg.No': regno_data[i].text,
            'Reg.Date': reg_date_data[i].text,
            'First Party': first_party_data[i].text,
            'Second Party': second_party_data[i].text,
            'Property Address': property_address_data[i].text,
            'Area (sq. ft.)': area,
            'Deed Type': deed_type_data[i].text,
            'Property Type': property_type_data[i].text,       
        }
        data.append(tmp)






# -------------------------------------------- MAIN CODE STARTS HERE ------------------------------------------------




# Select locality to scrap data for:
i = 1
for current_locality in all_localities[1:]:
    print(f"{i} : {current_locality}")
    i += 1

locality_num = int(input("Select locality you want to scrap data for: "))


# DRIVER SETUP--------------------------------------------------------------------------------------------------:
path = '/Users/dell/Downloads/chromedriver'
driver = webdriver.Chrome(path)

driver.get('https://esearch.delhigovt.nic.in/Complete_search.aspx')





# INPUT HANDLING------------------------------------------------------------------------------------------------:
sro_dropdown = Select(driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_ddl_sro_s'))
sro_dropdown.select_by_visible_text('Central -Asaf Ali (SR III)')

locality_dropdown = Select(driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_ddl_loc_s'))
locality_dropdown.select_by_visible_text(all_localities[locality_num])

year_input_dropdown = Select(driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_ddl_year_s'))
year_input_dropdown.select_by_visible_text('2021-2022')

print("INPUT DATA HANDELED!!!!!!")






# CAPTCHA HANDLING----------------------------------------------------------------------------------------------:

# keep decoding the captcha until it gets submitted successfully:
while True:
    time.sleep(5)           # wait for image to load:

    IMAGE_PATH = '//*[@id="ctl00_ContentPlaceHolder1_UpdatePanel4"]/div/img'
    captcha_image_element = driver.find_element(By.XPATH, IMAGE_PATH)
    driver.execute_script("arguments[0].scrollIntoView();", captcha_image_element)

    screenshot_bytes = captcha_image_element.screenshot_as_png        # save captcha image:
    with open("image.png", "wb") as f:
        f.write(screenshot_bytes)

    captcha_element = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_txtcaptcha_s"]')    # captcha box: 
    captcha_element.clear()  

    time.sleep(2)
    captcha_text = decode().upper()                 # decode captcha
    captcha_element.send_keys(captcha_text)         # send captcha input
    print(captcha_text)


    # Submit data:
    search_button = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btn_search_s')
    search_button.click()
    
    # Validate submission:
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print('INCORRECT CAPTCHA. RETRYING!!!!!!!!!!')
        time.sleep(3)
    except NoAlertPresentException:
        print('CORRECT CAPTCHA. SUBMITTING!!!!!!!!!!')
        time.sleep(3)
        break

    
print("SUBMITTED SUCCESSFULLY!!!!!!!!!!!!!")
time.sleep(6)          # wait for data to be loaded on screen












# SCRAPE THE TABLE--------------------------------------------------------------------------------------------------:

# check if table exists:
table = driver.find_elements(By.XPATH, "/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody")
if table:
    print("Table found. Extracting data !!!!!!!!!!!!!!!!!!!!")
else:
    print("Table NOT found. Exiting !!!!!!!!!!!!!!!!!!!!")
    sys.exit()


# Extract the table elements:
regno_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[1]/span')
reg_date_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[2]/span')

first_party_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[3]/span')
second_party_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[4]/span')

property_address_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[5]/span')
area_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[6]/span')

deed_type_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[7]/span')
property_type_data = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr/td[8]/span')


# Store the table data after data cleaning (converting to proper units):
data = []

# testing
limit = driver.find_elements(By.XPATH, '/html/body/form/div[3]/div[4]/div/center/div/div/div[2]/div/table/tbody/tr[13]/td/span/span[2]')
print(limit[0])
limit = int(limit[0].text)

print("Max pages available = ", limit)

cur_page = 1
while cur_page <= limit-1:
    
    get_data(data)
    
    # find the next button using its XPath
    next_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_gv_search_ctl13_Button2")
    
    # click the next button
    next_button.click()
    time.sleep(2)

    print(f"Page : {cur_page} extracted.")
    cur_page += 1


df = pd.DataFrame(data)     # create data frame
df.to_excel(f"table_data_{all_localities[locality_num]}.xlsx", index=False)        # transfer into excel file


print("DATA EXTRACTED SUCCESSFULLY !!!!!!!!!!!!!!!!!!!!!")







# QUIT SERVER--------------------------------------------------------------------------------------------------------:
driver.quit()
