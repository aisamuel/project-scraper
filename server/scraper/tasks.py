import requests
from bs4 import BeautifulSoup
from celery import shared_task
from .models import Product

AMAZON_URL = "https://www.amazon.com/s?k={brand}"

@shared_task
def scrape_amazon_products(brand):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    url = AMAZON_URL.format(brand=brand)
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        product_elements = soup.select('.s-main-slot .s-result-item')

        for product in product_elements:
            title_element = product.select_one('h2 a span')
            price_element = product.select_one('.a-price-whole')
            link_element = product.select_one('h2 a')
            
            if title_element and price_element and link_element:
                title = title_element.text.strip()
                price = price_element.text.strip()
                link = "https://www.amazon.com" + link_element['href']
                
                # Save product to the database
                Product.objects.create(
                    name=title,
                    price=price,
                    link=link,
                    brand=brand
                )
    else:
        print(f"Failed to retrieve data from {url}")
