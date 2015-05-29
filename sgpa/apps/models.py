import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from test.test_support import args_from_interpreter_flags
from django.db.models.fields import CharField, IntegerField, BooleanField
from django.template.defaultfilters import default
import base64

    
class Roles(models.Model):
    """
    Modelo para almacenar los roles posibles.
    """
    descripcion = models.CharField(max_length=200, unique=True)
    estado = models.BooleanField(default = 1)
    sistema = BooleanField(default = False)
    def __str__(self):
        return self.descripcion

class Users_Roles(models.Model):
    """
    Modelo que asocia un usuario con un rol
    """
    user = models.ForeignKey(User)
    role = models.ForeignKey(Roles)
    def __str__(self):
        return self.role

class Permisos(models.Model):
    """
    Modelo para almacenar los permisos
    """
    descripcion = models.CharField(max_length=50)
    tag = models.CharField(max_length=50)
    estado = models.BooleanField(default = False)
    sistema = BooleanField(default = False)
    def __str__(self):
        return self.descripcion

class Permisos_Roles(models.Model):
    """
    Modelo que asocia un rol con un permiso
    """
    roles = models.ForeignKey(Roles)
    permisos = models.ForeignKey(Permisos)

class Estados_Scrum(models.Model):
    """
    Estados Iniciado, Asignado, No Asignado, Pendiente, Finalizado y Cancelado de los User Stories 
    """
    descripcion = models.CharField(max_length = 50)
    def __str__(self):
        return self.descripcion

class Proyectos(models.Model):
    """
    Modelo para almacenar los datos de los proyectos
    """
    nombre = models.CharField(max_length = 50)
    #fecha de inicio
    fecha_ini = models.DateField()
    #fecha estimada de finalizacion
    fecha_est_fin = models.DateField()
    descripcion = models.CharField(max_length = 400)
    observaciones = models.CharField(max_length = 400)
    nro_sprint = models.IntegerField(null=True)
    #los estados que puede usar son el 1 (Iniciado), 4 (Pendiente), 5 (Finalizado), 6 (Cancelado)
    estado = models.ForeignKey(Estados_Scrum, default = 4)
    fecha_ini_real = models.DateField(null=True)
    fecha_fin_real = models.DateField(null=True)
    
    def __str__(self):
        return self.nombre

    
class Equipo(models.Model):
    """
    Modelo que asocia Proyecto Usuario Rol
    """
    proyecto = models.ForeignKey(Proyectos)
    usuario  = models.ForeignKey(User)
    rol      = models.ForeignKey(Roles)
    def __str__(self):
        return self.proyecto
    
    
class Flujos(models.Model):
    """
    Modelo para almacenar los flujos
    """
    proyecto = models.ForeignKey(Proyectos, null=True, blank=True)
    descripcion = models.CharField(max_length = 50)
    plantilla = models.BooleanField(default = True)    
    estado = models.BooleanField(default = True)
    tamano = models.IntegerField(null = True)
    def __str__(self):
        return self.descripcion
    

class Actividades(models.Model):
    """
    Modelo para almacenar las actividades en un flujo
    """
    descripcion = models.CharField(max_length= 50)
    estado = models.BooleanField(default = True)
    flujo = models.ForeignKey(Flujos)
    plantilla = models.BooleanField(default = True)
    def __str__(self):
        return self.descripcion
    
class Estados(models.Model):
    """
    Estados de las actividades
    """
    descripcion = models.CharField(max_length = 50)
    
class Actividades_Estados(models.Model):
    """
    Asociacion de estados con actividades
    """
    actividad = models.ForeignKey(Actividades)
    estados = models.ForeignKey(Estados)

class Prioridad(models.Model):
    """
    Describe la Prioridad del User Story
    """
    descripcion = models.CharField(max_length=30)
    def __str__(self):
        return self.descripcion


class UserStory(models.Model):
    """
    Modelo para almacenar los User Stories
    """
    nombre = models.CharField(max_length = 50, null = True)
    #Controlar!
    descripcion = models.CharField(max_length = 120, null=True)
    codigo = models.CharField(max_length = 30)
    valor_Negocio = models.IntegerField(null = True)
    valor_Tecnico = models.IntegerField(null = True)
    prioridad = models.ForeignKey(Prioridad, null=True)
    tiempo_Estimado = models.IntegerField(default = 0)
    tiempo_Real = models.IntegerField(default = 0)
    sprint = models.IntegerField(default = 0)
    usuario_Asignado = models.IntegerField(default = 0, null = True)
    flujo = models.IntegerField(default = 0)
    proyecto = models.ForeignKey(Proyectos, null = True)
    #indica si el hu esta activo o inactivo
    estado = models.BooleanField(default = True)
    #fecha en que se crea el hu
    fecha_creacion = models.DateField(null = True)
    #fecha en el que un hu asignado a un flujo y sprint inicia su actividad
    fecha_inicio = models.DateField(null = True)
    #fecha de ultima modificacion del hu
    fecha_modificacion = models.DateField(null = True)
    #nro de la actividad de flujo en el que se encuentra el hu (ex: Desarrollo de Flujo 1)
    f_actividad = models.IntegerField(default = 0)
    #nro del estado de la actividad de flujo en que se encuentra el hu (ex: Doing de Desarrollo de Flujo 1)
    f_a_estado = models.IntegerField(default = 0)
    #posicion exacta en la que se encuentra un hu dentro de un flujo
    flujo_posicion = models.IntegerField(null = True)
    #indica si el User Story se ha finalizado 
    finalizado = models.BooleanField(default = False)
    #notas = models.CharField(max_length = 512, null = True)
    estado_scrum = models.ForeignKey(Estados_Scrum, null = True)
    motivo_cancelacion = models.CharField(max_length = 512, null = True)

class UserStoryVersiones(models.Model):
    """
    Model para almacenar las versiones de los User Stories
    """
    idv = models.IntegerField()
    nombre = models.CharField(max_length = 50, null = True)
    #Controlar!
    version = models.IntegerField(null = True)
    descripcion = models.CharField(max_length = 120, null = True)
    codigo = models.CharField(max_length = 30)
    valor_Negocio = models.IntegerField(null = True)
    valor_Tecnico = models.IntegerField(null = True)
    prioridad = models.ForeignKey(Prioridad, null=True)
    tiempo_Estimado = models.IntegerField(default = 0)
    tiempo_Real = models.IntegerField(default = 0)
    sprint = models.IntegerField(null = True)
    usuario_Asignado = models.IntegerField(default = 0, null = True)
    flujo = models.IntegerField(default = 0)
    proyecto = models.ForeignKey(Proyectos, null = True)
    estado = models.BooleanField(default = True)
    fechahora = models.DateTimeField(null = True)
    usercambio = models.ForeignKey(User, null = True)
    f_actividad = models.IntegerField(default = 0)
    f_a_estado = models.IntegerField(default = 0)
    flujo_posicion = models.IntegerField(null = True)
    #indica si el User Story se ha finalizado 
    finalizado = models.BooleanField(default = False)
    #notas = models.CharField(max_length = 512, null = True)
    estado_scrum = models.ForeignKey(Estados_Scrum, null = True)
    motivo_cancelacion = models.CharField(max_length = 512, null = True)
    
class UserStoryRegistro(models.Model):
    """
    Model para guardar los registros de actividades de un HU
    """
    idr = models.IntegerField()
    descripcion_tarea = models.CharField(max_length = 256)
    
    nombre = models.CharField(max_length = 50, null = True)
    #Controlar!!
    version = models.IntegerField(null = True)
    descripcion = models.CharField(max_length = 120, null = True)
    codigo = models.CharField(max_length = 30)
    valor_Negocio = models.IntegerField(null = True)
    valor_Tecnico = models.IntegerField(null = True)
    prioridad = models.ForeignKey(Prioridad, null=True)
    tiempo_Estimado = models.IntegerField(default = 0)
    tiempo_Real = models.IntegerField(default = 0)
    sprint = models.IntegerField(null = True)
    usuario_Asignado = models.IntegerField(default = 0, null = True)
    flujo = models.IntegerField(default = 0)
    proyecto = models.ForeignKey(Proyectos, null = True)
    estado = models.BooleanField(default = True)
    fechahora = models.DateTimeField(null = True)
    usercambio = models.ForeignKey(User, null = True)
    f_actividad = models.IntegerField(default = 0)
    f_a_estado = models.IntegerField(default = 0)
    #notas = models.CharField(max_length = 512, null = True)
    estado_scrum = models.ForeignKey(Estados_Scrum, null = True)
    motivo_cancelacion = models.CharField(max_length = 512, null = True)
    
class UserStoryLog(models.Model):
    
    idl = models.ForeignKey(UserStory)
    nombre = models.CharField(max_length = 50, null = True)
    descripcion = models.CharField(max_length = 120, null = True)
    codigo = models.CharField(max_length = 30)
    flujo = models.ForeignKey(Flujos, null = True)
    f_actividad = models.IntegerField(default = 0)
    f_a_estado = models.IntegerField(default = 0)
    flujo_posicion = models.IntegerField(null = True)
    fechahora = models.DateTimeField(null = True)
    tiempoEstado = models.DateTimeField(null = True)
    usuario_Asignado = models.IntegerField(default = 0, null = True)
    sprint = models.IntegerField(null = True)

class Notas(models.Model):
    """
    Model para almacenar las notas de un User Story
    """
    hu = models.ForeignKey(UserStory)
    user = models.ForeignKey(User)
    descripcion = models.CharField(max_length = 256)
    fechahora = models.DateTimeField(null = True)
    def __str__(self):
        return self.descripcion
    
class Sprint(models.Model):
    """
    Modelo para almacenar los Sprints
    """
    proyecto = models.ForeignKey(Proyectos, null=True, blank=True)
    nro_sprint = models.IntegerField()
    #estados:
    #0 = todavia no empieza
    #1 = esta en progreso
    #2 = finalizado
    estado = models.IntegerField(null=True)
    fecha_ini = models.DateField(null=True)
    fecha_est_fin = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    #duracion en semanas
    duracion = models.IntegerField(default = 0)

class Dia_Sprint(models.Model):
    """
    Modelo para almacenar los datos de los dias de cada Sprint
    """
    sprint = models.ForeignKey(Sprint, null=True, blank=True)
    tiempo_estimado = models.IntegerField()
    tiempo_real = models.IntegerField()
    dia = models.IntegerField(null=True)
    fecha = models.DateField(null=True)

class archivoAdjunto(models.Model):
    #archivo = models.FileField(upload_to="adjunto")
    archivo = models.TextField(blank=True)
    hu = models.ForeignKey(UserStory, null=True, blank=True)
    filename = models.CharField(max_length = 100, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True);
    version = models.IntegerField(default = 1)
    actual = models.BooleanField(default = True)
    
    def __unicode__(self):
        """Representacion unicode del objeto"""
        return self.archivo.name    
    
    def set_data(self, data):
        self.archivo = base64.encodestring(data)
 
    def get_data(self):
        return base64.decodestring(self.archivo)
 
    data = property(get_data, set_data)
    
class historialResponsableHU(models.Model):
    hu = models.ForeignKey(UserStory)
    responsable = models.ForeignKey(User)

class horas_usuario_sprint(models.Model):
    """
    Modelo que permite relacionar un usuario y sus horas de trabajo con un sprint
    """
    horas = models.IntegerField(default = 0)
    usuario = models.ForeignKey(User)
    Sprint = models.ForeignKey(Sprint)
    
class hu_sprint(models.Model):
    sprint = models.ForeignKey(Sprint)
    hu = models.ForeignKey(UserStoryVersiones)
    
class huVersion_sprint(models.Model):
    """
    Modelo que relaciona un Sprint de un proyecto con una version de un User Story
    """
    sprint = models.ForeignKey(Sprint)
    userStoryVersiones = models.ForeignKey(UserStoryVersiones)
