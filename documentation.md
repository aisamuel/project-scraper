# Project Documentation

This Amazon product scraper backend project is a Django application for scraping product data from Amazon and exposing it through a REST API. The application integrates **Celery** for task scheduling, periodic scraping jobs, and includes anti-scraping measures. The project is designed to efficiently fetch, cache, and serve data via the Django REST Framework (DRF).

### 1. Project Setup and Running Locally

To get started, follow these steps to set up the project on your local machine.

#### Requirements
- Python 3.8 or higher
- Redis (as the broker for Celery)
- Django and Django REST Framework

#### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/aisamuel/project-Scraper.git
   cd project-directory
   ```

2. **Install Dependencies**:
   Set up a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

### 2. Celery and Broker Setup

Celery is used for scheduling and managing background tasks, such as periodic scraping jobs. Redis is configured as the broker.

#### Steps

1. **Install Redis**:
   Install Redis locally:
   ```bash
   # On Linux:
   sudo apt-get install redis-server
   
   # On macOS:
   brew install redis
   ```

2. **Configure Celery**:
   In `settings.py`, set up Celery with Redis as the broker:
   ```python
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   ```

3. **Run Celery Worker**:
   Start a Celery worker to process tasks:
   ```bash
   celery -A product_scraper worker --loglevel=info
   ```

4. **Run Celery Beat**:
   To enable periodic tasks, start Celery Beat in a separate terminal:
   ```bash
   celery -A product_scraper beat --loglevel=info
   ```

### 3. Scheduling and Managing Periodic Tasks

Periodic tasks, such as scraping Amazon for product data, are scheduled using Celery Beat. The task configuration can be modified in Django’s `settings.py` or via the `celery.py` configuration file.

#### Configuration Example

In `celery.py`, set the periodic task to run every 6 hours:
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('product_scraper')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Schedule scraping task every 6 hours
    sender.add_periodic_task(
        crontab(hour='*/6'),  # Every 6 hours
        scrape_amazon_products.s(),
    )
```

### 4. Web Scraping Implementation

The scraping is implemented as a Celery task, which fetches product data from Amazon’s HTML structure. To handle Amazon’s anti-scraping mechanisms, the scraper includes the following measures:

- **Random User-Agent Rotation**: A random user-agent is used for each request to simulate requests from different browsers.
- **Proxies**: A list of proxies is cycled to prevent repeated requests from the same IP address.
- **Random Delays**: Random delays between requests reduce the chances of being detected as a bot.
- **Caching Responses**: Cached responses reduce the need for repeated requests, minimizing the load on Amazon’s servers and decreasing the risk of IP blocking.
- **Error Handling for CAPTCHA Detection**: When a CAPTCHA is detected, the scraper skips processing to avoid being blocked.

#### Task Example

Here’s a simplified version of the scraping task:
```python
@shared_task(bind=True, max_retries=3)
def scrape_amazon_products(self, brand_name):
    # Define the request parameters, user-agent rotation, and proxy settings
    brand_name = os.getenv('BRAND_NAME', 'iPhone')
    url = f"https://www.amazon.com/s?k={brand_name}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    proxies = {"http": random.choice(PROXIES)}

    try:
        # Send request and parse response
        response = requests.get(url, headers=headers, proxies=proxies)
        if "captcha" in response.text.lower():
            raise Exception("Captcha encountered")
        
        # Parse products and store in database
        # ...

    except Exception as e:
        raise self.retry(exc=e)
```

### 5. Assumptions and Design Decisions

The project assumes a reliable network and access to Redis and Celery for task scheduling. Here are some key design choices and assumptions made in this project:

1. **Data Source**: Amazon is the source for product data, and the scraper relies on specific HTML structures.

2. **Celery and Redis for Task Management**: Celery is used with Redis as the broker due to its reliability and ease of setup. Celery enables scalable task management, allowing future expansion if scraping needs grow.

3. **Rate Limiting and Anti-Scraping**: To avoid IP blocks, requests are randomized with delays, proxies, and user-agent rotation. This design limits requests to Amazon, balancing data retrieval and compliance with Amazon’s access rules.

4. **Database Constraints**: Product data uses the ASIN as a unique identifier, ensuring no duplicate entries in the database. This assumption helps maintain data integrity.

5. **Caching Strategy**: Cached responses prevent redundant scraping, reducing the risk of triggering anti-scraping mechanisms and optimizing resource usage.

---

This documentation provides a foundational overview of setting up, running, and managing the backend, including web scraping, Celery setup, and task scheduling.