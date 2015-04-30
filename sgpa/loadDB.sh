#!/bin/bash


#echo "El password debe ser 'sergio' sin las comillas simples. Se pedira dos veces"

dropdb djangodb
#dropuser sergio  -U postgres
#createuser -d -l -P -r -S sergio -U postgres

if [ $? -ne 0 ]; then
    echo -e "\nSi ocurrio un error del tipo"
    #echo -e "\t\t'la autentificaci?n password fall? para el usuario <<postgres>>'"
    exit
fi

#echo -e "\n\nUsuario creado con exito."
echo "Ahora se creara la BD"
psql -U postgres postgres -f createDB.sql

#Make Migrations
echo "manage.py makemigrations"
./manage.py makemigrations 

#Migrate
echo "manage.py migrate"
./manage.py migrate

#Populate
echo "manage.py population"
./manage.py population

#tests
./manage.py test
