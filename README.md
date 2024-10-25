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
    
Install project dependencies:

    $ pip install -r requirements.txt   
    
Then simply apply the migrations:

    $ python manage.py makemigrations  

    $ python manage.py migrate

Then run test:

    $ python manage.py test
    

You can now run the development server:

    $ python manage.py runserver



# Client Side
    $ cd client
    
Run the server;

    $ python3 -m http.server 8020