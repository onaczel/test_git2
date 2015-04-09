import os
from __builtin__ import True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

import django
django.setup()

from django.contrib.auth.models import User
from apps.models import Users_Roles, Flujos, Roles, Actividades

def populate():
    add_roles('Administrador')
    add_roles('Usuario')
    add_roles('Scrum Master')
    add_roles('Cliente')
    
    add_user('admin', 'a123', 'deserver123@gmail.com', 1)
    
    add_flujo('Plantilla Generica')

def add_roles(descripcion):
    rol = Roles()
    rol.descripcion = descripcion
    rol.estado = True
    rol.save()
    return rol

def add_user(username, password, email, role):
    user = User()
    user.username = username
    user.set_password(password)
    user.email = email
    user.save()
    add_users_roles(user.id, role)
    return user

def add_users_roles(user_id, role_id):
    ur = Users_Roles()
    ur.role_id = role_id
    ur.user_id = user_id
    ur.save()
    return ur

def add_flujo(descripcion):
    flujo = Flujos()
    flujo.descripcion = descripcion
    flujo.plantilla = True
    flujo.estado = True
    flujo.save()
    actividades = ['Analisis', 'Diseno', 'Programacion', 'Testing', 'Despliegue']
    for act in actividades:
        add_actividades(act, flujo.id)
    return flujo

def add_actividades(descripcion, flujo_id):
    actividades = Actividades()
    actividades.descripcion = descripcion
    actividades.estado = True
    actividades.plantilla = True
    actividades.flujo_id = flujo_id
    actividades.save()
    return actividades

if __name__ == '__main__':
    print "Starting population script..."
    populate()
    print "Done."
    