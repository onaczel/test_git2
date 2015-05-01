#!/bin/bash

#Debe estar logueado como usuario root para correr este archivo
chmod 755 manage.py

#Make Migrations
echo "manage.py makemigrations"
./manage.py makemigrations apps

#Migrate
echo "manage.py migrate"
./manage.py migrate

#Populate
echo "manage.py population"
./manage.py population

#tests
./manage.py test

#runserver
./manage.py runserver
