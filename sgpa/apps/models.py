import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from test.test_support import args_from_interpreter_flags
from django.db.models.fields import CharField, IntegerField
from django.template.defaultfilters import default

    
class Roles(models.Model):
    """
    Modelo para almacenar los roles posibles.
    """
    descripcion = models.CharField(max_length=200, unique=True)
    estado = models.BooleanField(default = 1)
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
    def __str__(self):
        return self.descripcion

class Permisos_Roles(models.Model):
    """
    Modelo que asocia un rol con un permiso
    """
    roles = models.ForeignKey(Roles)
    permisos = models.ForeignKey(Permisos)
    
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
    
class UserStory(models.Model):
    """
    Modelo para almacenar los User Stories
    """
    descripcion = models.CharField(max_length = 50)
    codigo = models.IntegerField()
    valorNegocio = models.IntegerField()
    valorTecnico = models.IntegerField()
    prioridad = models.ForeignKey(Prioridad)
    tiempoEstimado = models.IntegerField()
    tiempoReal = models.IntegerField()
    sprint = models.IntegerField()
    usuarioAsignado = models.IntegerField()
    flujo = models.IntegerField()
    proyecto = models.ForeignKey(Proyectos)
    
    


    
    
#User.add_to_class('roles', models.ForeignKey(Users_Roles))
