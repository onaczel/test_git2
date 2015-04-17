import os
from __builtin__ import True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

import django
django.setup()

from django.contrib.auth.models import User
from apps.models import Users_Roles, Flujos, Roles, Actividades, Permisos, Permisos_Roles,\
    Prioridad

def populate():
    add_roles('Administrador')
    add_roles('Usuario')
    add_roles('Scrum Master')
    add_roles('Cliente')
    
    add_user('admin', 'a123', 'deserver123@gmail.com', 1)
    
    add_flujo('Plantilla Generica')
    
    permisos = ['Crear Usuario', 'Modificar Usuario', 'Eliminar Usuario', 'Crear Proyecto', 'Modificar Proyecto', 'Asignar Participantes a Proyecto', 'Eliminar Participantes de Proyecto', 'Crear User Stories', 'Modificar User Stories', 'Eliminar User Stories', 'Crear Plantilla de Flujos', 'Modificar Plantilla de Flujos', 'Eliminar Plantilla de Flujos', 'Planificar Sprints', 'Visualizar Proyectos', 'Crear Roles', 'Modificar Roles', 'Eliminar Roles']
    c=1
    for p in permisos:
        add_permisos(p)
        add_permisos_roles(c, 1)
        c = c + 1
    
    permisos_usuario = [15]
    permisos_scrum_master = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    permisos_cliente = [15]
    
    for p in permisos_usuario:
        add_permisos_roles(p, 2)
    for p in permisos_scrum_master:
        add_permisos_roles(p, 3)
    for p in permisos_cliente:
        add_permisos_roles(p, 4)
    
    add_prioridad('Baja')
    add_prioridad('Media')
    add_prioridad('Alta')
        
    
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

def add_permisos(descripcion):
    permisos = Permisos()
    permisos.descripcion = descripcion
    permisos.tag = 'tag'
    permisos.estado = True
    permisos.save()
    return permisos

def add_permisos_roles(permiso_id, rol_id):
    permiso_rol = Permisos_Roles()
    permiso_rol.roles_id = rol_id
    permiso_rol.permisos_id = permiso_id
    permiso_rol.save()
    return permiso_rol

def add_prioridad(descripcion):
    prioridad = Prioridad()
    prioridad.descripcion = descripcion
    prioridad.save()

if __name__ == '__main__':
    print "Starting population script..."
    populate()
    print "Done."
    