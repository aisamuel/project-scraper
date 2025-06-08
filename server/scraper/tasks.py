import logging
import os
import random
import time
from typing import List, Optional

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from celery import shared_task  # type: ignore
from django.core.cache import cache  # type: ignore
from django.db.utils import IntegrityError  # type: ignore

from utility import get_headers, get_proxies

from .models import Brand, Product

# Initialize logger for Celery tasks
logger = logging.getLogger("scraper")

# Constants
CACHE_TIMEOUT: int = 6 * 3600  # 6 hours
CAPTCHA_IDENTIFIER: str = os.getenv("CAPTCHA_IDENTIFIER", "captcha")


def fetch_page(
    url: str, headers: dict, proxies: Optional[dict], cache_key: str
) -> Optional[BeautifulSoup]:
    cached_response = cache.get(cache_key)
    if cached_response:
        logger.info(f"Using cached data for {cache_key}")
        return BeautifulSoup(cached_response, "lxml")

    try:
        logger.info(f"Making HTTP request to {url}")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)

        if CAPTCHA_IDENTIFIER in response.text:
            logger.warning("CAPTCHA detected; skipping this request.")
            return None

        cache.set(cache_key, response.content, timeout=CACHE_TIMEOUT)
        return BeautifulSoup(response.content, "lxml")

    except requests.exceptions.RequestException as exc:
        logger.error(f"Request failed: {exc}")
        raise exc


def parse_products(soup: BeautifulSoup, brand: Brand) -> None:
    product_elements = soup.select(".s-main-slot .s-result-item")
    for product in product_elements:
        title_elem = product.select_one(
            "a.a-link-normal.s-line-clamp-2.s-link-style.a-text-normal h2 span"
        )
        asin = product.get("data-asin")
        image_elem = product.select_one(".s-image")

        if asin and title_elem and image_elem:
            title = title_elem.text.strip()
            image = image_elem["src"]
            sku = "N/A"

            existing: Optional[Product] = Product.objects.filter(asin=asin).first()
            if existing:
                existing.name = title
                existing.sku = sku
                existing.image = image  # type: ignore
                existing.save()
                logger.info(f"Updated existing product {title} with ASIN {asin}")
            else:
                try:
                    Product.objects.create(
                        name=title, asin=asin, sku=sku, image=image, brand=brand
                    )
                    logger.info(f"Saved product {title} with ASIN {asin}")
                    time.sleep(random.uniform(1, 3))
                except IntegrityError:
                    logger.warning(
                        f"Product with ASIN {asin} already exists, skipping."
                    )


def has_next_page(soup: BeautifulSoup) -> bool:
    return soup.select_one("a.s-pagination-next") is not None


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_amazon_products(self) -> None:
    brands = Brand.objects.all()

    for brand in brands:
        brand_name = brand.name
        logger.info(f"Starting scraping for brand: {brand_name}")

        brand, _ = Brand.objects.get_or_create(name=brand_name)

        page = 1
        more_pages = True
        headers = get_headers()
        proxies = get_proxies()

        while more_pages:
            cache_key = f"amazon_{brand_name}_page_{page}"
            url = f"{os.getenv('AMAZON_BASE_URL', 'https://www.amazon.com/')}/s?k={brand_name}&page={page}"

            try:
                soup = fetch_page(url, headers, proxies, cache_key)
                if soup is None:
                    return

                parse_products(soup, brand)
                more_pages = has_next_page(soup)
                if more_pages:
                    page += 1
                    logger.info(f"Moving to next page: {page}")

            except Exception as exc:
                logger.error(f"Error scraping {brand_name} page {page}: {exc}")
                self.retry(exc=exc)
