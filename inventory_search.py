# Use web-scraping in order to fetch the current car inventory.
# For this purpose, I will be using the help of the selenium library
# which will automate the process of browsing the inventory web app
# as a normal user would do it.

import os
import re
import time
import csv
from cs50 import SQL

# With selenium already installed, import the required modules:
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Define function login which opens CRM URL and enters credentials:
def login():

    try:
        # Define the url of the login page:
        login_url = "https://autogermana.crm2.dynamics.com"

        # Credentials:
        username = os.environ['BMW_USERNAME']
        password = os.environ['BMW_PASSWORD']

        # Open the login url:
        driver.get(login_url)

        # Define explicit wait:
        wait = WebDriverWait(driver, 30)

        print("Trying to log in...")

        # Find the username input field and the submit button:
        username_input = wait.until(
            EC.visibility_of_element_located((By.ID, "i0116")))
        submit_username = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#idSIButton9")))

        # Type the username in its corresponding field and click submit button:
        username_input.send_keys(username)
        submit_username.click()

        # Find the password input field and the submit button:
        password_input = wait.until(
            EC.visibility_of_element_located((By.ID, "i0118")))
        submit_password = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#idSIButton9")))

        # Type the password and submit it:
        password_input.send_keys(password)
        submit_password.click()

        # Click yes when asked to remain logged in:
        driver.find_element(By.ID, "idSIButton9").click()

    except Exception as error:
        print(f"Error loging in: {error}")
        return
    else:
        print("Log in succesful")
        return

# Create function that navigates through the webpage until finding the car inventory list:
def navigate_to_cars():

    try:
        wait = WebDriverWait(driver, 90)

        print("Navigating to car inventory...")

        # Click the button to access CRM as a sales representative:
        wait.until(EC.frame_to_be_available_and_switch_to_it('AppLandingPage'))
        crm_enter_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#AppModuleTileSec_1_Item_1")))
        crm_enter_button.click()
        driver.switch_to.default_content()

        # Find the button to enter the vehicle inventory and click it:
        vehicles_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#sitemap-entity-NewSubArea_07aae866")))
        vehicles_button.click()

    except Exception as error:
        print(f"Error Navigating to car inventory: {error}")
        return
    else:
        print("Succesfuly navigated to car inventory")
        return

# Create function to extract the info of the cars in the inventory from the main container:
def extract_car_info_from_container():

    try:
        wait = WebDriverWait(driver, 60)

        print("Extracting car inventory...")

        scrollable = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[class='ag-body-viewport ag-row-no-animation ag-layout-normal']")))

        # Create list of dictionaries to store all the information of a car:
        car_list = []

        # Get the total number of cars registered in the invenotry:
        cars_paging = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[role='status']"))).text
        numbers = re.findall(r'\d+', cars_paging)
        cars_total = int(numbers[2])
        page_total = int(numbers[1])
        page_start = int(numbers[0])

        # Initialize car_count for counting the # of cars registered in the car_list:
        car_count = 0

        while car_count < cars_total:

            # Loop in the current page for getting car data until the page total number of cars is reached:
            while car_count < page_total:

                # Locate the principal container that shows the whole car inventory list:
                vh_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ag-center-cols-container")))

                # Check if the current window of rows is visible before trying to extract their info:
                try:
                    vh_container.find_element(By.CSS_SELECTOR, f"div[row-index='{car_count - page_start + 1}']")
                    try:
                        vh_container.find_element(
                            By.CSS_SELECTOR, f"div[row-index='{(car_count - page_start + 1) + 14}']")
                    except Exception:
                        if vh_container.find_element(By.CSS_SELECTOR, f"div[row-index='{(page_total - page_start + 1) - 1}']"):
                            pass

                    # Loop through the next 15 car data rows and extract their data:
                    a = car_count - page_start + 1
                    for i in range(a, a + 15):

                        # Locate the row that contain car information and use it to extract the info from it:
                        try:
                            car = vh_container.find_element(
                                By.CSS_SELECTOR, f"div[row-index='{i}']")
                        except Exception:
                            break

                        # Extract all the info from a car element and add it to the car_list:
                        car_dict = {}
                        car_dict["prod_month"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='ce_mesdeproduccinconfirmado']").text
                        car_dict["model"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_modelid']").text
                        car_dict["version"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='ce_version']").text
                        car_dict["color"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_paintingcode']").text
                        car_dict["order_num"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_ordernumber']").text
                        car_dict["chasis_num"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_name']").text
                        car_dict["model_year"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_modelyear']").text
                        car_dict["location"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='ce_ubicaconintegracion']").text
                        car_dict["price"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_customerprice']").text
                        car_dict["upholstery"] = car.find_element(
                            By.CSS_SELECTOR, "div[col-id='huddle_upholsterycode']").text
                        car_list.append(car_dict)

                        # Update car data counter:
                        car_count += 1

                except Exception:
                    # Scroll to show the next group of cars
                    driver.execute_script("arguments[0].scrollBy(0, 300);", scrollable)
                    time.sleep(2)
                    continue
                
            if car_count < cars_total:
                # Change to new page:
                next_page_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Página siguiente']")
                next_page_button.click()

                # Scroll back to the top of the page:
                driver.execute_script("arguments[0].scrollTop = 0;", scrollable)
                time.sleep(3)

                # Update Page_total variable:
                cars_paging = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[role='status']"))).text
                numbers = re.findall(r'\d+', cars_paging)
                page_total = int(numbers[1])
                page_start = int(numbers[0])
                # update cars_total in case a car was sold whle the code was running:
                cars_total = int(numbers[2])

    except Exception as error:
        print(f"Error extracting car inventory: {error}")
        return
    else:
        print("Succesfuly extracted car inventory")
        print(f"{len(car_list)} cars registered.")
        return car_list
    
def create_database(data, update_time, db_name):
    
    db = SQL(f'sqlite:///{db_name}')

    db.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            prod_month TEXT,
            model TEXT NOT NULL,
            version TEXT,
            color TEXT NOT NULL,
            order_num TEXT NOT NULL,
            chasis_num TEXT NOT NULL,
            model_year INTEGER,
            location TEXT,
            price INTEGER,
            upholstery TEXT
        )''')

    db.execute('''
        CREATE TABLE IF NOT EXISTS time (
            time_stamp REAL
        )''')

    db.execute('DELETE FROM inventory')
    db.execute('DELETE FROM time')

    db.execute('INSERT INTO time (time_stamp) VALUES (?)', update_time)

    # Insert data into the table
    print("reading database...")
    i = 0
    for row in data:
        db.execute('INSERT INTO inventory (prod_month,model,version,color,order_num,chasis_num,model_year,location,price,upholstery) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   row['prod_month'], row['model'], row['version'], row['color'], row['order_num'], row['chasis_num'], row['model_year'], row['location'], row['price'], row['upholstery'])
        i += 1
        print(f'Entry #:{i}/{len(data)}')

if __name__ == "__main__":

    # Start a Selenium Session:
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)

    # Login in the CRM app using the login() function:
    login()

    # Navigate to the part of the app that shows the car list:
    navigate_to_cars()

    # Extract car info:
    car_inventory = extract_car_info_from_container()

    # Store the current time to show is as a time stamp of the last inventory update:
    update_time = time.time()

    # Close Session:
    driver.quit()

    # Write inventory to CSV file:    
    with open('car_inventory.csv', 'w', newline='') as csv_file:
        # Use the keys of the first dictionary as fieldnames
        fieldnames = car_inventory[0].keys()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        csv_writer.writeheader()  # Write the header row
        
        for row in car_inventory:
            csv_writer.writerow(row)  # Write each dictionary as a row

    #Create sqlite database:
    create_database(car_inventory, update_time, '/mnt/d/CURSOS/CS50/Final Project/CS50-final-project/car_inventory.db')
