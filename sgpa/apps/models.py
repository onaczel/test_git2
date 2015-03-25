import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from test.test_support import args_from_interpreter_flags

    
class Roles(models.Model):
    descripcion = models.CharField(max_length=200)
    estado = models.BooleanField(default = 1)
    def __str__(self):
        return self.descripcion

class Users_Roles(models.Model):
    user = models.ForeignKey(User)
    role = models.ForeignKey(Roles)
    def __str__(self):
        return self.role

class Permisos(models.Model):
    descripcion = models.CharField(max_length=50)
    tag = models.CharField(max_length=50)
    def __str__(self):
        return self.descripcion

class Permisos_Roles(models.Model):
    roles = models.ForeignKey(Roles)
    permisos = models.ForeignKey(Permisos)

#User.add_to_class('roles', models.ForeignKey(Users_Roles))