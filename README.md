Django Project Tracker API
  Python 3.x  
- Django (LTS version recommended)  
- Django REST Framework  
- SQLite (default)

Authentication

This project uses Token Authentication provided by Django REST Framework.  outh

Installation Guide

Clone the repository
Create Virtual Environment
Install required packages
    pip install django djangorestframework
settings.py:

INSTALLED_APPS = [
       'rest_framework',
    'rest_framework.authtoken',
    'tracker',  #app name
]

python manage.py migrate

python manage.py createsuperuser
python manage.py runserver




