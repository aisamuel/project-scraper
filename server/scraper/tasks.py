import time
import random
import requests
import os
from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger
from fake_useragent import UserAgent
from .models import Product, Brand
from django.core.cache import cache
from django.db.utils import IntegrityError

# Initialize logger for Celery tasks
logger = get_task_logger(__name__)

# Constants
CACHE_TIMEOUT = 6 * 3600  # Cache each page result for 6 hours
CAPTCHA_IDENTIFIER = os.getenv('CAPTCHA_IDENTIFIER', 'captcha')
PROXY_LIST = []

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_amazon_products(self):
    brand_name = os.getenv('BRAND_NAME', 'iPhone')
    
    # # Set up headers
    try:
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": "en-US,en;q=0.5"
        }
    except:
        # If fake_useragent fails, use the fallback
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5"
        }

    # Rotate proxy for each request
    if PROXY_LIST:
        proxy = random.choice(PROXY_LIST)
        proxies = {"http": proxy, "https": proxy}

    # Start at the first page and increment until no "Next" page is available
    page = 1
    more_pages = True

    # Retrieve or create the Brand in the database
    brand, created = Brand.objects.get_or_create(name=brand_name)
    if created:
        logger.info(f"Created a new brand entry for {brand_name}")

    while more_pages:
        print(page)
        cache_key = f"amazon_{brand_name}_page_{page}"
        cached_response = cache.get(cache_key)

        if cached_response:
            logger.info(f"Using cached data for {brand_name}, page {page}")
            soup = BeautifulSoup(cached_response, "lxml")
        else:
            # Make a request to Amazon if cache is empty
            url = f"{os.getenv('AMAZON_BASE_URL', '')}s?k={brand_name}&page={page}"
            print(url)
            try:
                if PROXY_LIST:
                    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                else:
                    response = requests.get(url, headers=headers, timeout=10)

                if CAPTCHA_IDENTIFIER in response.text:
                    logger.warning("CAPTCHA detected; skipping this request.")
                    return

                # Cache the HTML content of this page
                cache.set(cache_key, response.content, timeout=CACHE_TIMEOUT)
                soup = BeautifulSoup(response.content, "lxml")

            except requests.exceptions.RequestException as exc:
                logger.error(f"Request failed for {brand_name}, page {page}: {exc}")
                self.retry(exc=exc)

            except Exception as exc:
                logger.error(f"An error occurred while scraping for {brand_name}, page {page}: {exc}")
                raise exc

        # Parse product data
        product_elements = soup.select('.s-main-slot .s-result-item')

        for product in product_elements:
            title_element = product.select_one('h2 a span')
            asin_element = product.get('data-asin')
            sku_element = product.get('data-sku')
            image_element = product.select_one('.s-image')


            if asin_element and title_element and image_element:
                # Check if the product already exists in the database to prevent duplicates
                if Product.objects.filter(asin=asin_element).exists():
                    logger.info(f"Product with ASIN {asin_element} already exists, skipping.")
                    continue

                title = title_element.text.strip()
                asin = asin_element
                sku = "N/A"
                image = image_element['src']

                try:
                    # Save product to the database
                    Product.objects.create(
                        name=title,
                        asin=asin,
                        sku=sku,
                        image=image,
                        brand=brand,
                    )
                    logger.info(f"Saved product {title} with ASIN {asin}")
                    
                    # Random delay to avoid detection
                    time.sleep(random.uniform(1, 3))
                    
                except IntegrityError:
                    logger.warning(f"Product with ASIN {asin} already exists, skipping.")

        # Check if a "Next" page link is available
        next_page = soup.select_one("a.s-pagination-next")
        print(next_page)
        if next_page:
            page += 1  # Go to the next page
            logger.info(f"Moving to the next page: {page}")
        else:
            more_pages = False  # End loop if there are no more pages
