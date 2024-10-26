# Amazon Scraper

# Introduction

The goal of this project is to provide minimalist amazon brand Scraper application using Vue js and Django Rest Framework.

# Amazon Scraper

# Getting Started

First clone the repository from Github and switch to the new directory:

    $ git clone https://github.com/aisamuel/project-Scraper.git



# Server Side
    $ cd server
    
Activate the virtualenv for your project.

    $ source env/bin/activate  

Create a .env file in /server folder and copy the content of .env_sample file into it.

Install project dependencies:

    $ pip install -r requirements.txt   
    
Then simply apply the migrations:

    $ python manage.py makemigrations  

    $ python manage.py migrate

Then run test:

    $ python manage.py test
    

You can now run the development server:

    $ python manage.py runserver


Install Redis locally or use a cloud-based Redis service:
   ```bash
   # On Linux:
   sudo apt-get install redis-server
   
   # On macOS:
   brew install redis
   ```

In `settings.py`, set up Celery with Redis as the broker:
   ```python
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   ```


Start a Celery worker to process tasks:
   ```bash
   celery -A product_scraper worker --loglevel=info
   ```


To enable periodic tasks, start Celery Beat in a separate terminal:
   ```bash
   celery -A product_scraper beat --loglevel=info
   ```



# Client Side
    $ cd client
    
Run the server;

    $ python3 -m http.server 8020

Go to http://localhost:8020/