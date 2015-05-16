#!/bin/bash

#Debe estar logueado como usuario postgres para correr este archivo



dropdb djangodb -U postgres
#dropdb djangodbprod -U postgres

#dropuser sergio  -U postgres
#createuser -d -l -P -r -S sergio -U postgres

if [ $? -ne 0 ]; then
    exit
fi


#echo -e "\n\nUsuario creado con exito."
echo "Ahora se creara la BD"
psql -U postgres postgres -f createDB.sql



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
