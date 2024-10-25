import time
import random
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger
from fake_useragent import UserAgent
from .models import Product, Brand
from django.db.utils import IntegrityError

# Initialize logger for Celery tasks
logger = get_task_logger(__name__)

# Constants
AMAZON_URL = "https://www.amazon.com/s?k={brand}"
CAPTCHA_IDENTIFIER = "captcha"
RATE_LIMIT_WAIT = 60  # Wait time in seconds if a rate limit is detected
PROXY_LIST = [
    # "http://proxy1.com:port",
    # "http://proxy2.com:port",
    # # Add more proxies here
]

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_amazon_products(self, brand_name):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,  # Rotate user-agent on each task execution
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    # Rotate proxy for each request
    if PROXY_LIST:
        proxy = random.choice(PROXY_LIST)
        proxies = {"http": proxy, "https": proxy}

    url = AMAZON_URL.format(brand=brand_name)

    try:
        # Make a request to Amazon
        if PROXY_LIST:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        else:
            response = requests.get(url, headers=headers, timeout=10)

        print(response.text)
        
        # Detect CAPTCHA or rate limiting
        if CAPTCHA_IDENTIFIER in response.text:
            logger.warning("CAPTCHA detected; skipping this request.")
            return  # Skip processing if CAPTCHA is detected
        
        # Log successful connection
        log_message = f"Successfully connected to Amazon for brand: {brand_name}"
        if PROXY_LIST:
            log_message += f"using proxy: {proxy}"
        logger.info(log_message)

        soup = BeautifulSoup(response.content, "lxml")
        product_elements = soup.select('.s-main-slot .s-result-item')

        # Retrieve or create the Brand
        brand, created = Brand.objects.get_or_create(name=brand_name)
        if created:
            logger.info(f"Created a new brand entry for {brand_name}")

        print(product_elements)

        for product in product_elements:
            title_element = product.select_one('h2 a span')
            asin_element = product.get('data-asin')
            sku_element = product.get('data-sku')  # Placeholder; modify as needed
            image_element = product.select_one('.s-image')

            if title_element and asin_element and image_element:
                title = title_element.text.strip()
                asin = asin_element
                sku = sku_element or "N/A"
                image = image_element['src']

                try:
                    # Save product to the database
                    Product.objects.create(
                        name=title,
                        asin=asin,
                        sku=sku,
                        image=image,
                        brand=brand
                    )
                    logger.info(f"Saved product {title} with ASIN {asin}")
                    
                    # Random delay to avoid detection
                    time.sleep(random.uniform(1, 3))
                    
                except IntegrityError:
                    logger.warning(f"Product with ASIN {asin} already exists, skipping.")
        
    except requests.exceptions.RequestException as exc:
        logger.error(f"Request failed for {brand_name}: {exc}")
        self.retry(exc=exc)  # Retry the task if a network error occurs

    except Exception as exc:
        logger.error(f"An error occurred while scraping Amazon for {brand_name}: {exc}")
        raise exc
