from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

import dotenv

dotenv.read_dotenv(os.path.join(os.path.dirname(
    os.path.dirname(__file__)), '.env'), override=True)
    
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_scraper.settings')

app = Celery('product_scraper')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'


app.conf.beat_schedule = {
    'scrape_amazon_products_every_six_hours': {
        'task': 'scraper.tasks.scrape_amazon_products',
        # 'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'schedule': crontab(minute='*'),  # Runs every minute
    },
}