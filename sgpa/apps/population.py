import os
from __builtin__ import True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

import django
django.setup()

from django.contrib.auth.models import User
from apps.models import Users_Roles, Flujos, Roles, Actividades, Permisos, Permisos_Roles,\
    Prioridad

def populate():
    add_roles('Administrador', True)
    add_roles('Usuario', True)
    add_roles('Scrum Master', False)
    add_roles('Cliente', False)
    
    add_user('admin', 'a123', 'deserver123@gmail.com', 1)
    
    add_flujo('Plantilla Generica')
    
    permisos = ['Crear Usuario', 'Modificar Usuario', 'Eliminar Usuario', 'Crear Roles', 'Modificar Roles', 'Eliminar Roles','Crear Proyecto', 'Modificar Proyecto', 'Crear Plantilla de Flujos', 'Modificar Plantilla de Flujos', 'Eliminar Plantilla de Flujos', 'Asignar Participantes a Proyecto', 'Eliminar Participantes de Proyecto', 'Crear User Stories', 'Modificar User Stories', 'Eliminar User Stories', 'Planificar Sprints', 'Visualizar Proyectos']
    tags = ['CU', 'MU', 'EU', 'CR', 'MR', 'ER', 'CP', 'MP','CPF', 'MPF', 'EPF', 'APP', 'EPP', 'CUS', 'MUS', 'EUS', 'PS', 'VP']
    sistema = [True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False]
    c=1
    for p in permisos:
        add_permisos(p, tags[c-1], sistema[c-1])
        add_permisos_roles(c, 1)
        c = c + 1
    
    permisos_usuario = [15]
    permisos_scrum_master = [12, 13, 14, 15, 16, 17, 18 ]
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
        
    
def add_roles(descripcion, sistema):
    rol = Roles()
    rol.descripcion = descripcion
    rol.estado = True
    rol.sistema = sistema
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

def add_permisos(descripcion, tag, sistema):
    permisos = Permisos()
    permisos.descripcion = descripcion
    permisos.tag = tag
    permisos.estado = True
    permisos.sistema = sistema
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
    