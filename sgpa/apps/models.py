import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from test.test_support import args_from_interpreter_flags
from django.db.models.fields import CharField
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

class Flujos(models.Model):
    """
    Modelo para almacenar los flujosc
    """
    descripcion = models.CharField(max_length = 50)
    estado = models.BooleanField(default = True)

class Actividades(models.Model):
    """
    Modelo para almacenar las actividades en un flujo
    """
    descripcion = models.CharField(max_length= 50)
    flujo = models.ForeignKey(Flujos)
    
class Estados(models.Model):
    descripcion = models.CharField(max_length = 50)
    
class Actividades_Estados(models.Model):
    actividad = models.ForeignKey(Actividades)
    estados = models.ForeignKey(Estados)
    
#User.add_to_class('roles', models.ForeignKey(Users_Roles))