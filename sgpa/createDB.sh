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

