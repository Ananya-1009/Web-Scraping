from asyncio import wait
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="web_scraping"
)

cursor = conn.cursor()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
print(driver.capabilities['browserVersion'])
driver.quit()

# Configure ChromeOptions to ignore SSL certificate errors
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--start-maximized') 

# Initialize WebDriver with ChromeOptions
driver = webdriver.Chrome(options=chrome_options)

# Open the webpage
url = 'https://www.nobroker.in/' 
driver.get(url)

try:
    # Function to select an option based on user input
    def select_option(option_text):
        wait = WebDriverWait(driver, 20)
        # Locate the option based on the text and class
        element = wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "cursor-pointer") and contains(text(), "{option_text}")]')))
        element.click()
        print(f"Selected option: {option_text}")
    def rent_select(option_text):
        element=wait.until(EC.element_to_be_clickable((By.XPATH,f'//div[contains(@class, "cursor-pointer") and contains(text(), "{option_text}")]')))
        element.click()

    # Simulate user input for selecting an option ('Rent', 'Buy', or 'Commercial')
    user_choice = "buy"
    city="Noida" 
    localities = [
    "Sector 62",
    "Sector 63",
    "Indirapuram"]

    # Map user input to display text on the website
    choice_map = {
        'rent': 'Rent',
        'buy': 'Buy',
        'commercial': 'Commercial'
    }

    # Validate user input and select the corresponding option
    if user_choice in choice_map:
        if user_choice=="rent":
            rent_select(choice_map[user_choice])
        else:
            select_option(choice_map[user_choice])
    else:
        raise ValueError("Invalid choice. Please enter 'rent', 'buy', or 'commercial'.")
except ValueError as ve:
     print(f"Error: {ve}")

except Exception as e:
    print(f"An error occurred: {e}")


def select_city(city_name):
    wait = WebDriverWait(driver, 30)

    # Open dropdown
    dropdown = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".nb-select__value-container"))
    )
    dropdown.click()

    # Type city name
    input_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[id*='react-select'][id$='-input']")
        )
    )

    input_box.send_keys(Keys.CONTROL, "a")
    input_box.send_keys(Keys.DELETE)
    input_box.send_keys(city_name)

    # Let React populate results
    options = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "nb-select__option"))
    )

    for i, option in enumerate(options):
        if city_name.lower() in option.text.lower():
            if i > 0:
                input_box.send_keys(Keys.ARROW_DOWN * (i-1))
            input_box.send_keys(Keys.ENTER)
            return

    print("City selected:", city_name)

def add_localities(localities):
    wait = WebDriverWait(driver, 20)

    for locality in localities:
        input_box = wait.until(
            EC.element_to_be_clickable((By.ID, "listPageSearchLocality"))
        )

        input_box.click()
        input_box.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        input_box.send_keys(locality)

        dropdown = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "autocomplete-dropdown-container")
            )
        )
        suggestions = dropdown.find_elements(By.XPATH, "./div")

        if not suggestions:
            raise Exception(f"No suggestions found for: {locality}")

        suggestions[0].click()

        time.sleep(0.5)
def search():
    
    wait = WebDriverWait(driver, 20)

    search_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'prop-search-button')]")
        )
    )
    search_btn.click()
def extract():
    last_height = driver.execute_script("return document.body.scrollHeight")
    wait = WebDriverWait(driver, 10)
    skip_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.='Skip'] | //span[.='Skip']"))
    )
    skip_btn.click()

    last_count = 0

    for _ in range(50):
        # Scroll down slowly
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1.5)

        # Remove any blocking overlays
        driver.execute_script("""
        document.querySelectorAll('*').forEach(e => {
            if (getComputedStyle(e).position === 'fixed' && e.offsetHeight > 300) {
                e.remove();
            }
        });
        """)

        # Count loaded cards
        cards = driver.find_elements(By.CSS_SELECTOR, "div.nb__2_XSE")
        current_count = len(cards)

        # Stop if no new cards loaded
        if current_count == last_count:
            print("Reached end of results.")
            break

        last_count = current_count
    cards = driver.find_elements(By.CSS_SELECTOR, "div.nb__2_XSE")
    print("Loaded cards:", current_count)
    for i in range(len(cards)):
        try:
            address_el= cards[i].find_element(By.XPATH,".//*[contains(@class,'overflow-ellipsis') and contains(@class,'whitespace-nowrap')]")
            address = address_el.text.strip()
            price_el = cards[i].find_element(By.XPATH,".//div[contains(@class,'flex-col') and contains(@class,'items-center') and contains(@class,'w-33pe')]")
            price_container = price_el.text.strip()
            lines = price_container.split("\n")
            price=lines[0]
            price_per_sqft = lines[1] if len(lines) > 1 else None

            cursor.execute("""
                INSERT IGNORE INTO properties (address, price, price_per_sqft)
                VALUES (%s, %s, %s)
            """, (address, price, price_per_sqft))

        except Exception as e:
            print("Skipping one card:", e)

    conn.commit()

WebDriverWait(driver, 30).until(
    lambda d: d.execute_script('return document.readyState') == 'complete'
)
print("Page fully loaded")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print("Number of iframes:", len(iframes))
for index, frame in enumerate(iframes):
    print(index, frame.get_attribute("id"), frame.get_attribute("name"))
select_city(city)

add_localities(localities)
search()
extract()
time.sleep(2) 


