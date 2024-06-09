import time
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Database connection
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='arka@1256',
        database='amazon',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def create_table_if_not_exists():
    connection = connect_db()
    with connection.cursor() as cursor:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            price VARCHAR(50),
            rating VARCHAR(50),
            reviews_count VARCHAR(50),
            availability VARCHAR(255),
            url TEXT
        );
        """
        cursor.execute(create_table_sql)
    connection.close()

def store_product_data(product_data):
    connection = connect_db()
    with connection.cursor() as cursor:
        sql = """
        INSERT INTO products (name, price, rating, reviews_count, availability, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            product_data['name'],
            product_data['price'],
            product_data['rating'],
            product_data['reviews_count'],
            product_data['availability'],
            product_data['url']
        ))
        connection.commit()
    connection.close()

def scrape_amazon_product(url):
    # Setup Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for faster scraping
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # Open the URL
    driver.get(url)
    time.sleep(3)  # Wait for the page to load completely

    # Parse the page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract product data
    try:
        name = soup.find(id='productTitle').get_text(strip=True)
    except AttributeError:
        name = "N/A"

    try:
        price = soup.find('span', {'class': 'a-offscreen'}).get_text(strip=True)
    except AttributeError:
        price = "N/A"

    try:
        rating = soup.find('span', {'class': 'a-icon-alt'}).get_text(strip=True)
    except AttributeError:
        rating = "N/A"

    try:
        reviews_count = soup.find('span', {'id': 'acrCustomerReviewText'}).get_text(strip=True)
    except AttributeError:
        reviews_count = "N/A"

    try:
        availability = soup.find('div', {'id': 'availability'}).get_text(strip=True)
    except AttributeError:
        availability = "N/A"

    product_data = {
        'name': name,
        'price': price,
        'rating': rating,
        'reviews_count': reviews_count,
        'availability': availability,
        'url': url
    }

    # Close the browser
    driver.quit()

    # Store the product data in the database
    store_product_data(product_data)
    print(f"Product data for '{name}' has been stored in the database.")

if __name__ == "__main__":
    create_table_if_not_exists()
    product_url = input("Enter the Amazon product URL: ")
    scrape_amazon_product(product_url)
