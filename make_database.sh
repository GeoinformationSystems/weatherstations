#!/bin/bash

# DO NOT WRITE 'rm ... -r' ANYWHERE IN HERE !!!

# re-create databasee
sudo -u postgres dropdb climatecharts_weatherstations
sudo -u postgres createdb climatecharts_weatherstations

# migrate db model
python manage.py makemigrations
python manage.py migrate
