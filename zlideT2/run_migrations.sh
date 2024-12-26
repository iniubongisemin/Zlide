#!bin/bash

python manage.py makemigrations
echo "makemigrations"
python manage.py migrate
echo "migrate"
gunicorn auth.wsgi
