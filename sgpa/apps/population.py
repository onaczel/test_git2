import os
from __builtin__ import True
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')

import django
django.setup()

from django.contrib.auth.models import User
from apps.models import Users_Roles, Flujos, Roles, Actividades, Permisos, Permisos_Roles,\
    Prioridad, Estados, Proyectos, Equipo, Estados_Scrum, UserStory

def populate():
    add_roles('Administrador', True)
    add_roles('Usuario', True)
    add_roles('Scrum Master', False)
    add_roles('Cliente', False)
    add_roles("developer", False)
    add_roles("observador", False)
    
    add_user('Administrador', 'General', 'admin', 'a123', 'deserver123@gmail.com', 1)
    add_user('Joaquin', 'Quintana', 'jquin', 'a123', 'rokkaie@gmail.com', 2)
    add_user('Ariel', 'Diaz', 'lastdeo', 'a123', 'lastdeo@gmail.com', 2)
    add_user('Jorge', 'Rojas', 'jrojas', 'a123', 'jrojas@gmail.com', 2)
    add_user('Raul', 'Bobadilla', 'rbob', 'a123', 'rbob@gmail.com', 2)
    add_user('Hector', 'Roa', 'hroa', 'a123', 'hroa@gmail.com', 2)
    add_user('Victor', 'Figueredo', 'vfir', 'a123', 'vfif@gmail.com', 2)
    add_user('Gregory', 'Andaluz', 'gram', 'a123', 'gram@gmail.com', 2)
    add_user('Walter', 'Amarilla', 'wam', 'a123', 'wam@gmail.com', 2)
    add_user('Horacio', 'Gimenez', 'hgim', 'a123', 'hgim@gmail.com', 2)
    add_user('German', 'Gonzalez', 'ggon', 'a123', 'ggon@gmail.com', 2)
    add_user('Karina', 'Franco', 'kfran', 'a123', 'kfran@gmail.com', 2)
    add_user('Claudia', 'Rios', 'crios', 'a123', 'crios@gmail.com', 2)
    add_user('Natalia', 'Aguero', 'nag', 'a123', 'nag@gmail.com', 2)
    
    add_flujo('Plantilla Generica')
    add_flujo('Plantilla Generica 2')
    add_flujo('Plantilla Generica 3')
    
    
    permisos = ['Crear Usuario', 'Modificar Usuario', 'Eliminar Usuario', 'Crear Roles', 'Modificar Roles', 'Eliminar Roles','Crear Proyecto', 'Modificar Proyecto', 'Crear Plantilla de Flujos', 'Modificar Plantilla de Flujos', 'Eliminar Plantilla de Flujos', 'Asignar Participantes a Proyecto', 'Eliminar Participantes de Proyecto', 'Crear User Stories', 'Modificar User Stories', 'Eliminar User Stories', 'Planificar Sprints', 'Visualizar Proyectos', 'Crear Roles en Proyecto', 'Modificar Roles en Proyecto', 'Eliminar Roles en Proyecto', 'Cambiar Estado User Story', 'Administrar Flujo Proyecto']
    tags = ['CU', 'MU', 'EU', 'CR', 'MR', 'ER', 'CP', 'MP','CPF', 'MPF', 'EPF', 'APP', 'EPP', 'CUS', 'MUS', 'EUS', 'PS', 'VP', 'CRP', 'MRP', 'ERP', 'CEUS', 'AFP']
    sistema = [True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False]
    c=1
    for p in permisos:
        add_permisos(p, tags[c-1], sistema[c-1])
        add_permisos_roles(c, 1)
        c = c + 1
    
    permisos_usuario = [18]
    permisos_scrum_master = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23 ]
    permisos_cliente = [18]
    permisos_developer = [15, 18, 22]
    permisos_observador = [18]
    
    for p in permisos_usuario:
        add_permisos_roles(p, 2)
    for p in permisos_scrum_master:
        add_permisos_roles(p, 3)
    for p in permisos_cliente:
        add_permisos_roles(p, 4)
    for p in permisos_developer:
        add_permisos_roles(p, 5)
    for p in permisos_observador:
        add_permisos_roles(p, 6)
    
    '''
    add_prioridad('Baja')
    add_prioridad('Media')
    add_prioridad('Alta')
    '''
        
    for i in range(1,11):
        add_prioridad(i)
    
    add_estado('To Do')
    add_estado('Doing')
    add_estado('Done')
    
    add_estado_scrum("Iniciado")
    add_estado_scrum("Asignado")
    add_estado_scrum("No Asignado")
    add_estado_scrum("Pendiente")
    add_estado_scrum("Finalizado")
    add_estado_scrum("Cancelado")
    
    add_proyecto("Proyecto 1")
    add_proyecto("Proyecto 2")
    add_proyecto("Proyecto 3")
    
    add_equipo(1, 3, 1)
    add_equipo(1, 4, 2)
    add_equipo(1, 5, 3)
    add_equipo(1, 6, 4)
    add_equipo(1, 5, 5)
    add_equipo(1, 5, 6)
    add_equipo(1, 5, 7)
    add_equipo(1, 5, 8)
    
    add_equipo(2, 3, 2)
    add_equipo(2, 4, 3)
    add_equipo(2, 5, 3)
    add_equipo(2, 5, 9)
    add_equipo(2, 5, 10)
    
    add_equipo(3, 3, 2)
    add_equipo(3, 4, 3)
    add_equipo(3, 5, 3)
    add_equipo(3, 5, 8)
    add_equipo(3, 5, 10)
    add_equipo(3, 5, 11)
    add_equipo(3, 5, 12)
    
    for h in range(1,10):
        add_hu(1, "hu" +str(h), "User Story "+str(h), "Como usuario debo poder realizar esta funcion "+str(h))
        add_hu(2, "hu" +str(h), "User Story "+str(h), "Como usuario debo poder realizar esta funcion "+str(h))
        add_hu(3, "hu" +str(h), "User Story "+str(h), "Como usuario debo poder realizar esta funcion "+str(h))
        
def add_estado_scrum(descripcion):
    estado = Estados_Scrum()
    estado.descripcion = descripcion
    estado.save()

def add_roles(descripcion, sistema):
    rol = Roles()
    rol.descripcion = descripcion
    rol.estado = True
    rol.sistema = sistema
    rol.save()
    return rol

def add_user(fname, lname, username, password, email, role):
    user = User()
    user.first_name = fname
    user.last_name = lname
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
    flujo.tamano = 15
    flujo.save()
    actividades = ['Analisis', 'Diseno', 'Programacion', 'Testing', 'Despliegue']
    for act in actividades:
        add_actividades(act, flujo.id, True)
    return flujo

def add_actividades(descripcion, flujo_id, plantilla):
    actividades = Actividades()
    actividades.descripcion = descripcion
    actividades.estado = True
    actividades.plantilla = plantilla
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
    
def add_estado(descripcion):
    estado = Estados()
    estado.descripcion = descripcion
    estado.save()

def add_proyecto(descripcion):
    proyecto = Proyectos()
    proyecto.nombre = descripcion
    proyecto.fecha_ini= '2015-05-01'
    proyecto.fecha_est_fin = '2015-06-02'
    proyecto.descripcion = 'una prueba de proyecto'
    proyecto.observaciones = 'ninguna'
    proyecto.nro_sprint = 0
    proyecto.save()
    add_flujo_proyecto(proyecto.id, 1)
    
def add_equipo(p_id, r_id, u_id):
    equipo = Equipo()
    equipo.proyecto_id = p_id
    equipo.rol_id = r_id
    equipo.usuario_id = u_id
    equipo.save()
    
def add_flujo_proyecto(proyecto_id, flujo_id):
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    flujo = Flujos.objects.get(pk=flujo_id)
    flujo_nuevo = Flujos()
    flujo_nuevo.descripcion = flujo.descripcion
    flujo_nuevo.estado = flujo.estado
    flujo_nuevo.plantilla = False
    flujo_nuevo.tamano = flujo.tamano
    flujo_nuevo.proyecto = proyecto
    flujo_nuevo.save()
    actividades = ['Analisis', 'Diseno', 'Programacion', 'Testing', 'Despliegue']
    for act in actividades:
        add_actividades(act, flujo_nuevo.id, False)
    
def add_hu(proyecto_id, codigo, nombre, descripcion):
    us = UserStory()
    us.nombre = nombre
    us.descripcion = descripcion
    us.codigo = codigo
    us.tiempo_Estimado = random.randint(20, 70)
    us.valor_Negocio = 5
    us.valor_Tecnico = 5
    us.prioridad = Prioridad.objects.get(pk=3)
    us.proyecto_id = proyecto_id
    us.estado_scrum = Estados_Scrum.objects.get(pk=3)
    us.save()

if __name__ == '__main__':
    print "Starting population script..."
    populate()
    print "Done."
    
