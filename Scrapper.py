from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import math

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def get_num_pages(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "valtech-carrefourar-search-result-0-x-totalProducts--layout"))
        )
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(8)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
        
        soup = BeautifulSoup(driver.page_source, "html.parser", from_encoding="utf-8")
        total_products_text = soup.find("div", class_="valtech-carrefourar-search-result-0-x-totalProducts--layout").find("span").text
        total_products = int(total_products_text.split(" ")[0])
        items_per_page = 16
        numeroPaginas = math.ceil(total_products / items_per_page)
        return numeroPaginas

    except Exception as e:
        print("Hubo un error al calcular el número de páginas: ", e)
        return 0

def scrape_page(url, page, data):
    try:
        driver.get(f"{url}?page={page}")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-product-summary-2-x-productBrand"))
        )
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser", from_encoding="utf-8")
        elements = soup.find_all("div", class_="valtech-carrefourar-product-summary-status-0-x-container")
        for element in elements:
            nombre = element.find("span", class_="vtex-product-summary-2-x-productBrand")
            elementprice = element.find("span", class_="valtech-carrefourar-product-price-0-x-currencyContainer")
            if nombre and elementprice:
                data.append({
                    "nombre": nombre.text.strip(),
                    "precio": elementprice.text.strip().replace("\xa0", " ")  # Reemplazar el carácter de espacio no separable
                })
    
    except Exception as e:
        print("Hubo un error al esperar los elementos: ", e)

def scrape_category(url):   
    data = []
    # numeroPaginas = get_num_pages(url)
    numeroPaginas = 1 # Para evitar problemas de detección de páginas, se fija a 50
    for page in range(1, numeroPaginas + 1):
        scrape_page(url, page, data)
    
    df = pd.DataFrame(data)
    return df

# Ejemplo de uso
try:
    df = scrape_category("https://www.carrefour.com.ar/Perfumeria")
    df.to_csv("elfile2.csv", encoding='utf-8', index=False)
    print(df)
finally:
    driver.quit()
