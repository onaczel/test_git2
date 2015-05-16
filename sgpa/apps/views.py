from django.shortcuts import get_object_or_404, render, render_to_response
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.template import RequestContext, loader
import time
import os
from django.views.static import serve
from django.core.servers.basehttp import FileWrapper

from apps.models import Roles, Users_Roles, Permisos, Permisos_Roles, Flujos, Actividades, Actividades_Estados, Proyectos, Equipo, UserStory, Sprint, Dia_Sprint, UserStoryVersiones, Prioridad,\
    Estados, UserStoryRegistro, archivoAdjunto, Estados_Scrum, Notas,\
    historialResponsableHU
from django.contrib.auth.models import User


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.core.context_processors import csrf, request

import user
from gc import get_objects
from django.contrib.redirects.models import Redirect
from gi.overrides.keysyms import blank
from django.forms.fields import RegexField
from cProfile import label
from django.db.models.fields import BooleanField
from django.contrib.sites import requests
from random import choice
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models.base import Model

from datetime import timedelta, date, datetime
from __builtin__ import int, str
from twisted.protocols.telnet import NULL
from django.core.exceptions import ObjectDoesNotExist
from _ast import Str
from django.forms.formsets import INITIAL_FORM_COUNT
from types import StringType
from django.conf import settings
import psycopg2
from psycopg2 import connect
from django.db import connection
import StringIO
from bsddb.dbtables import _data
from apps.commands import enviarMail, notificarNota, notificarModificacionHU,\
    notificarRegistroTrabajo, notificarCambioResponsableHU


######################################################################################################################################################

#####################################################################################################################################################

class IndexView(generic.DetailView):
    template_name='apps/index.html'
    def get(self, request, *args, **kwargs):
        return render_to_response(request, self.template_name)


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.Field(required=True)
    last_name = forms.Field(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2" )

    def save(self, commit=True):
        """
        Obtiene los datos del formulario creacion de usuario y registra el usuario en el sistema
        @param self:self
        @param commit:commit = True
        @return: User guardado  
        """
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.firs_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if user.is_superuser == 'null':
            user.is_superuser='FALSE'
        if commit:
            user.save()
        return user 

class UserModifyForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.Field(required=True)
    last_name = forms.Field(required=True)
    
    def __init__(self, *args, **kwargs):
        super(UserModifyForm, self).__init__(*args, **kwargs)
        del self.fields['username']
        
    class Meta:
        model = User
        
        fields = ("first_name", "last_name",  "email", "password1", "password2")
        

    def save(self, commit=True):
        """
        Obtiene los datos del formulario de modificacion de usuario y registra los cambios en el sistema
        @param self:self
        @param commit:commit = True
        @return: User guardado  
        """
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if user.is_superuser == 'null':
            user.is_superuser='FALSE'
        if commit:
            user.save()
        return user 
    
def nuevo_usuario(request, user_logged):
    """
    Verifica que el formulario es valido y almacena el nuevo usuario en la base de datos
    @param request: Http request
    @return: render a  apps/user_create.html, se le envia el formulario para registrar nuevo usuario y el contexto
    """
    if request.method=='POST':
        formulario = UserCreateForm(request.POST)
        if formulario.is_valid:
            formulario.save()
            #ur = Users_Roles()
            user = User()
            user = User.objects.get(username=formulario.cleaned_data['username'])
            #ur.user_id = user.id
            #if user.is_superuser:
            #    ur.role_id = 1
            #else:
            #    ur.role_id = 2
            #CONTROLAR!  
            user_id = user.id 
            #ur.save()
            roles = Roles.objects.all()
            return render_to_response('apps/user_assign_role.html',{'roles':roles, 'user_logged':user_logged, 'user_id':user_id,}, context_instance=RequestContext(request))
    else:
        formulario = UserCreateForm(initial={'email':'example@mail.com'})

    return render_to_response('apps/user_create.html', {'formulario':formulario, 'user_logged':user_logged}, context_instance=RequestContext(request))

def listroleuser(request, user_id):
    """
    Devuelve una lista de roles del sistema
    @param request: Http request
    @param user_id: Id de un usuario registrado en el sistema
    @return: render a  apps/user_assign_role.html, lista de roles, id del user, contexto
    """
    roles = Roles.objects.all()
    return render_to_response('apps/user_assign_role.html',{'roles':roles, 'user_id':user_id}, context_instance=RequestContext(request))

def asignarrolusuario(request, user_logged, user_id):
    """
    Asigna un rol a un usuario registrado en el sistema
    @param request: Http request
    @param user_id: Id de un usuario registrado en el sistema
    @return: render a  apps/user_created.html, contexto
    """
    roles = request.POST.getlist(u'roles')
    for r in roles:
        try:
            rol = Roles.objects.get(pk=r)
        except:
            rol = None
        ur = Users_Roles()
        ur.user_id = user_id
        ur.role_id = rol.id
        ur.save()
    
    return render_to_response('apps/user_created.html',{'user_logged':user_logged}, RequestContext(request))
  
    
def ingresar(request):
    """
    Metodo que permite el inicio de sesion en el sistema
    
    Verifica que el usuario este activo y lo redirige a su template correspondiente
    segun su rol en el sistema 
    
    @param request: Http request
    @return: render a template correspondiente segun rol del usuario en el sistema, contexto
    """
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:    
                    login(request, acceso)
    #'''Se trae de la base de datos el objeto usuario de la tabla User'''
                    user = User.objects.get(username=usuario)
    #'''Se compara con el registro en la tabla User_Roles'''
                    ur = Users_Roles.objects.get(user=user.id)
    #'''De la tabla de Roles se trae el id del rol del usuario'''
                    rol = Roles.objects.get(pk=ur.role_id)
    #'''Si el usuario es administrador'''
                    #if rol.id == 1:
                        #return HttpResponseRedirect('/apps/user_private_admin')
                    return render_to_response('apps/user_private_admin.html', {'usuario':user, 'rol_sistema':rol.sistema, 'rol_id':rol.id}, context_instance=RequestContext(request))
                    #return inicio(request, user.id, rol.id)
    #'''Si es usuario normal'''
                    #else:
                        
                        #return render_to_response('apps/user_private_user.html', {'listproyectos':listproyectos}, RequestContext(request))
                     #   return HttpResponseRedirect('/apps/user_private_user')
                else:
                    return render_to_response('apps/user_no_active.html', context_instance=RequestContext(request))
            else:
                return render_to_response('apps/user_no_exists.html', context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('apps/ingresar.html', {'formulario':formulario}, context_instance=RequestContext(request))


def inicio(request, user_id, role_id):
    """
    @param request: Http request
    @param user_id: id del Usuario dentro del Sistema
    @param role_id: id del Rol del Usuario
    @return: render a user_private_admin.html con el Usuario, el id y la condicion de sistema de su rol
    """
    rol = get_object_or_404(Roles, pk=role_id)
    user = get_object_or_404(User, pk=user_id)
    return render_to_response('apps/user_private_admin.html', {'usuario':user, 'rol_sistema':rol.sistema, 'rol_id':rol.id}, context_instance=RequestContext(request))

def recuperarContrasena(request):
        """
        Genera una nueva contrasena para un usuario activo registado en el sistema
        La nueva contrasena se envia via email al usuario en cuestion
        @param request: Http request
        @return: Si hay exito retorna render a apps/user_new_pwd.html y una instancia del contexto  
        """
        if request.method == 'POST':
                     
                usuario = request.POST['username']
          

                if User.objects.filter(username=usuario).exists():
                    user = User.objects.get(username = usuario)
                
                    longitud = 6
                    valores = "123456789abcdefghijklmnopqrstuvwxyz?*"
 
                    p = ""
                    p = p.join([choice(valores) for i in range(longitud)])
                
                    user.set_password(p)
                    user.save()
                    asunto = 'SGPA-Cambio de clave de accseso'
                    msg = 'Nueva clave de acceso para el usuario <'+usuario+'>: '+ p
                    list = []
                    list.append(user)
                    
                    enviarMail(asunto, msg, list)
                
                    return render_to_response('apps/user_new_pwd_ok.html', {'username':usuario},context_instance=RequestContext(request))
                
                else:               
                
                    return render_to_response('apps/user_pwd_user_not_valid.html', context_instance=RequestContext(request))
        
 
        return render_to_response('apps/user_new_pwd.html', context_instance=RequestContext(request)) 
    
'''
Cada vista debe tener una clase, o funcion
y un render que llame al template
'''
class newProject(generic.DetailView):
    template_name = 'apps/project_admin_new.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class modadmin(generic.DetailView):
    template_name = 'apps/admin_mod.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class modproyecto(generic.DetailView):
    template_name = 'apps/project_mod.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
'''
class adminuser(generic.DetailView):
    template_name="apps/user_admin.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
'''
class adminrole(generic.DetailView):
    template_name ='apps/role_admin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
'''
class adminproject(generic.DetailView):
    template_name = 'apps/project_admin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
'''
class adminflow(generic.DetailView):
    template_name = 'apps/flow_admin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    


    
    
##############################################################################################################################################

##############################################################################################################################################

def adminmod(request, user_logged):
    """
    obtiene el rol y los permisos del usuario
    @param request: Http
    @param user_logged: id del usuario logueado en el sistema
    @return: render a apps/admin_mod.html con el id del usuario, el id de su rol y la lista de sus permisos
    """
    permisos = misPermisos(user_logged, 0)
    rol_permiso = Users_Roles.objects.get(user_id = user_logged)
    rol = Roles.objects.get(pk=rol_permiso.role_id)
    return render_to_response('apps/admin_mod.html', {'misPermisos':permisos, 'user_logged':user_logged, 'rol_id':rol.id})
'''
def adminuser(request, user_id):
    permisos = misPermisos(user_id, 0)
    rol_permiso = Users_Roles.objects.get(user_id = user_id)
    rol = Roles.objects.get(pk=rol_permiso.role_id)
    return render_to_response('apps/user_admin.html', {'misPermisos':permisos, 'user_id':user_id, 'rol_id':rol.id})
'''
def listprojects(request, user_id):
    """
    Genera una lista de proyectos asociados a un usuario
    @param request: Http request
    @param user_id: Id de un usuario registrado en el sistema
    @return: render a  apps/project_mod.html, lista de proyectos asociados al usuario con id = user_id 
    """
    listproyectos = []
    equipo = Equipo.objects.filter(usuario_id=user_id)
    proyectos = Proyectos.objects.all()
    for eq in equipo:
        for p in proyectos:
            if eq.proyecto_id == p.id:
                listproyectos.append(Proyectos(p.id, p.nombre))
    #para que funcione el boton atras
    user= get_object_or_404(User, pk=user_id)
    rol_usuario = Users_Roles.objects.get(user_id = user.id)
    rol = get_object_or_404(Roles, pk=rol_usuario.role_id)
    return render_to_response('apps/project_mod.html', {'listproyectos':listproyectos, 'user_id':user.id, 'rol_id':rol.id})


def project(request, project_id):
    """
    Retorna el render a apps/project_front_page.html
    @param request: Http request
    @param project_id: Id de un proyecto registrado en el sistema
    @return: Retorna el render a apps/project_front_page
    """
    return render_to_response('apps/project_front_page.html')
                     


@login_required(login_url='apps/ingresar')
def privado(request):
    """
    Retorna el template correspondiente a un usuario con rol Administrador
    @param request:Http request
    @return: Retorna el template correspondiente a un usuario con rol Administrador
    
    """
    usuario = request.user
    return render_to_response('apps/user_private_admin.html', {'usuario':usuario}, context_instance=RequestContext(request))

@login_required(login_url='apps/ingresar')
def privadoNoadmin(request):
    """
    Retorna el template correspondiente a un usuario con rol Usuario
    @param request:Http request
    @return: Retorna el template correspondiente a un usuario con rol Usuario
    """
    usuario = request.user
    return render_to_response('apps/user_private_user.html', {'usuario':usuario}, context_instance=RequestContext(request))

@login_required(login_url='apps/ingresar')
def cerrar(request):
    """
    Recibe un request y cierra la sesion correspondiente
    @param request:Http request
    @return: render al template de login /apps/ingresar/
    """
    logout(request)
    return HttpResponseRedirect('/apps/ingresar/')

'''
Se debe crear una funcion que tome una request, y guarde en una variable
la lista de objetos en cuestion, luego enviar esa lista en un render to response
al html que trabajara con el.
Por supuesto, la funcion se debe encontrar en urls
'''
def listuser(request, user_logged):
    """
    @param request: Http request
    @param user_id: id del Usuario logueado
    @return: Retorna una lista con todos los usuarios del sistema y lo envia al template
    de modificacion de usuario  
    """
    permisos = misPermisos(user_logged, 0)
    rol_permiso = Users_Roles.objects.get(user_id = user_logged)
    rol = Roles.objects.get(pk=rol_permiso.role_id)
    
    user_logged =User.objects.get(pk=user_logged)
    
    users = User.objects.all()
    #return render_to_response("apps/user_admin.html", {"users":users})
    return render_to_response('apps/user_admin.html', {'misPermisos':permisos, 'user_logged':user_logged, 'rol_id':rol.id, 'users':users})

def listuserdel(request):
    """
    @param request: Http request
    @return: Retorna una lista con todos los usuarios del sistema y lo envia al template
    de eliminacion de usuario
    """
    users = User.objects.all()
    return render_to_response("apps/user_select_del.html", {"users":users})

def listrolesproj(request, proyecto_id):
    """
    @param request: Http request
    @return: Retorna una lista con todos los roles de proyectos y lo envia al template
    de modificacion de roles
    """
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    roles = Roles.objects.filter(sistema=False)
    user = request.user
    mispermisos = misPermisos(user.id, proyecto_id)
    return render_to_response("apps/role_admin_project.html", {"roles":roles, 'proyecto':proyecto, 'misPermisos':mispermisos,  'user_logged':user.id, 'guardado':False, 'proyectonombre':proyecto.nombre})
'''
def listrolesdel(request):
    """
    @param request: Http request
    @return: Retorna una lista con todos los roles del sistema y lo envia al template
    de eliminacion de roles
    """
    roles = Roles.objects.all()
    return render_to_response("apps/role_delete.html", {"roles":roles})
'''





def rolecreateproj(request, proyecto_id):
    """
    @param request: Http request
    @param proyecto_id: id del proyecto actual
    @return: render a apps/role_set_permisos.html, lista de permisos, el id y la descripcion del rol que se creo recientemente
    """
    proyectonombre = Proyectos.objects.get(pk = proyecto_id).nombre
    user = request.user
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    mispermisos =misPermisos(request.user.id, proyecto_id)
    if request.method == 'POST':
        form = RoleModifyForm(request.POST)
        if form.is_valid():
            form.save()
        #role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role = Roles.objects.latest('id')
        role.sistema = False
        role.save()
        role_id = role.id
        permisos = Permisos.objects.filter(sistema = False)
        return render_to_response("apps/role_set_permisos_proj.html", {'proyecto':proyecto, "permisos":permisos, "role_id":role_id, "role_descripcion":role.descripcion, 'proyectonombre':proyectonombre}, context_instance=RequestContext(request))
    else:
        form = RoleModifyForm()
    
    return render_to_response('apps/role_create_proj.html' ,{'form':form, 'proyecto':proyecto, 'misPermisos':mispermisos, 'user_logged':user.id, 'proyecto_b':True, 'proyectonombre':proyectonombre}, context_instance=RequestContext(request))

def asignarrolproj(request, proyecto_id, role_id):
    """
    Funcion para asignar permisos a un rol creado
    @param request: Http
    @param proyecto_id: id del proyecto actual
    @param role_id: id del rol al que se asignaran permisos
    @return: render a apps/role_admin_project.html con la lista de roles, el id del proyecto, la lista de permisos del usuario, el id del usuario logueado, y un booleano que indica el exito de la accion
    """
    proyectonombre = Proyectos.objects.get(pk=proyecto_id).nombre
    r = Roles.objects.get(pk = role_id)
    if setpermisos(request, r) == None:
        #error
        print "error"
    
    
    roles = Roles.objects.filter(sistema = False)
    user = request.user
    mispermisos = misPermisos(user.id, proyecto_id)
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    return render_to_response("apps/role_admin_project.html", {"roles":roles, 'proyecto':proyecto, 'misPermisos':mispermisos, 'user_logged':user.id, 'guardado':True, 'proyectonombre':proyectonombre})

def rolemodifyproj(request, proyecto_id, role_id):
    """
    Modifica un rol del sistema
    @param request: Http request
    @param role_id: Id de un rol registrado en el sistema
    @return: render a apps/role_set_permisos_mod.html con una lista de permisos, el id y la descripcion del rol
    """
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    rol = get_object_or_404(Roles, pk=role_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    if request.method == 'POST':
        form = RoleModifyForm(request.POST)
        if form.is_valid():
            rol.descripcion = form.cleaned_data['descripcion']
            rol.save()
        #return render_to_response("apps/role_set_permisos_mod.html", {"role_id":rol.id, "role_descripcion":rol.descripcion}, context_instance=RequestContext(request))
        return rolemodifypermisos(request, 0, rol.id, proyecto_id)
    else:
        form = RoleModifyForm(initial={'descripcion':rol.descripcion})
    
    return render_to_response('apps/role_modify_form.html' ,{'form':form, 'proyecto_id':proyecto.id, 'proyectonombre':proyecto.nombre, 'misPermisos':mispermisos, "rol":rol, 'user_logged':0, 'proj':True}, context_instance=RequestContext(request))
    
def roledeleteproj(request, proyecto_id, role_id):
    """
    Establece el estado de un rol a False
    @param request: Http request
    @param proyecto_id: id del proyecto actual
    @param role_id: Id de un rol registrado en el sistema
    
    @return: render a apps/role_deleted.html
    """
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    r = get_object_or_404(Roles, pk=role_id)
    
    r.estado = False
    r.save()
    
    roles = Roles.objects.filter(estado = True, sistema=False)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    
    return render_to_response("apps/role_admin_project.html", {"roles":roles, 'misPermisos':mispermisos, 'proyecto':proyecto, 'eliminado':True})


def muser(request, user_logged, user_id):
    """
    Metodo que obtiene los campos modificados del formulario de modificacion de usuario
    @param request: Http request
    @param user_id: Id de un usuario registrado en el sistema  
    @return: render a apps/user_modified.html, contexto
    """
    user = get_object_or_404(User, pk=user_id)
    if request.POST:
        form = UserModifyForm(request.POST)
        if form.is_valid():
            #user.save(update_field=['username'])
            user.set_password(form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            #form.save()
            return render_to_response("apps/user_modified.html", {'user_logged':user_logged},RequestContext(request))
    else:
        form = UserModifyForm(initial={ 'email':user.email, 'first_name':user.first_name, 'last_name':user.last_name})
        
        
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    user_logged_name = request.user
    user_logged = User.objects.get(username = user_logged_name)
    
    return render_to_response('apps/user_form_mod.html', {'form':form, 'user_logged':user_logged.id}, context_instance=RequestContext(request))

def eliminaruser(request):
    """
    @param request: Http request
    @return: render a apps/user_select_del.html con el request  
    """
    return render(request, 'apps/user_select_del.html')

def deluser(request, user_logged, user_id):
    """
    Pone como inactivo a un usuario registrado en el sistema
    @param request: Http request
    @param id: Id de un usuario registrado en el sistema
    @return: render a apps/user_deleted.html con el contexto
    """
    u = get_object_or_404(User, pk=user_id)

    u.is_active = False
    u.save()
    
    return render_to_response("apps/user_deleted.html",{'user_logged':user_logged}, RequestContext(request))


     
#########################################################################################################################################################

#######################################################################################################################################################
class RoleCreateForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = ("descripcion", "sistema")

class RoleModifyForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = ("descripcion",)
        
#Noreversematch es un error de configuracion de url
def listpermisos(request, user_logged):
    """
    @param request: Http request
    @param user_logged: id del Usuario logueado en el sistema
    @return: render a apps/role_set_permisos.html, lista de permisos, el id y la descripcion del rol que se creo recientemente
    """
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
        role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role_id = role.id
        permisos = []
        if role.sistema == True:
            permisos = Permisos.objects.filter(sistema = True)
        else:
            permisos = Permisos.objects.filter(sistema = False)
        return render_to_response("apps/role_set_permisos.html", {"permisos":permisos, "role_id":role_id, "role_descripcion":role.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
    else:
        form = RoleCreateForm()
    
    #permisos = misPermisos(user_logged, 0)
     
    return render_to_response('apps/role_create.html' ,{'form':form, 'user_logged':user_logged}, context_instance=RequestContext(request))
#MAnager isn't accesible via model isntances, no se pude acceder desde un modelo a 
#una instancia de una clase
def asignarrol(request, user_logged, role_id):
    """
    Asocia una lista de permisos con un rol
    @param request: Http request
    @param user_logged: id del Usuario logueado en el sistema
    @param role_id: Id de un rol registrado en el sistema
    @return: render a  apps/role_created.html con el contexto 
    """
    r = get_object_or_404(Roles, pk=role_id)
    sistema = r.sistema
    setpermisos(request, r)
        
    return render_to_response("apps/role_created.html", {'sistema':sistema, 'user_logged':user_logged}, context_instance = RequestContext(request))

def setpermisos(request, role):
    """
    Funcion que asigna una lista de permisos a un rol
    @param request: Http
    @param role: objeto Rol al que seran asignados los permisos
    @return: objeto Permisos_Roles con la lista de permisos asociados al rol
    """
    permrol = None
    lista = request.POST.getlist(u'permisos')
    for p in lista:
        try:
            #permiso = Permisos.objects.get(descripcion=p)
            permiso = Permisos.objects.get(pk=p)
        except Permisos.DoesNotExist:
            permiso = None
        permrol = Permisos_Roles()
        permrol.roles_id = role.id
        permrol.permisos_id = permiso.id
        permrol.save()
    
    
    return permrol
    
    

def listrolesmod(request, user_logged):
    """
    @param request: Http request
    @ret14urn: Retorna una lista con todos los roles del sistema y lo envia al template
    de modificacion de roles
    """
    roles = Roles.objects.all()
    permisos = misPermisos(user_logged, 0)
    return render_to_response("apps/role_admin.html", {"roles":roles, 'user_logged':user_logged, 'misPermisos':permisos})

def rolemodify(request, user_logged, role_id):
    """
    Modifica un rol del sistema
    @param request: Http request
    @param role_id: Id de un rol registrado en el sistema
    @return: render a apps/role_set_permisos_mod.html con una lista de permisos, el id y la descripcion del rol
    """
    rol = get_object_or_404(Roles, pk=role_id)
    if request.method == 'POST':
        form = RoleModifyForm(request.POST)
        if form.is_valid():
            rol.descripcion = form.cleaned_data['descripcion']
            rol.save()
        #return render_to_response("apps/role_set_permisos_mod.html", {"role_id":rol.id, "role_descripcion":rol.descripcion}, context_instance=RequestContext(request))

        return rolemodifypermisos(request, user_logged, rol.id, 0)
    else:
        form = RoleModifyForm(initial={'descripcion':rol.descripcion})
    
    return render_to_response('apps/role_modify_form.html' ,{'form':form, "rol":rol , 'user_logged':user_logged, 'proyecto_id':0}, context_instance=RequestContext(request))
    
def rolemodifypermisos(request, user_logged, role_id, proyecto_id):
    """
    obtiene la lista de permisos de un rol, los modifica, y los guarda
    @param request:Http
    @param user_logged: id del usuario logueado en el sistema
    @param role_id: id del rol a ser modificado
    @param proyecto_id: id del proyecto actual
    @return: render a role_set_permisos mod_proj: con la lista de permisos, el rol, el id del usuario, el id del proyecto
    @return: render a role_set_permisos_mod: con la lista de permisos, el id del rol, su descripcion, y el usuario logueado
    """
    rol = get_object_or_404(Roles, pk=role_id)

    permisos = Permisos.objects.all()
    proles = Permisos_Roles.objects.all()
    inicializarPermisos()
    for p in permisos:
        for ur in proles:
            if ur.roles_id == rol.id and ur.permisos_id == p.id:
                p.estado = True
                p.save()
                
    if rol.sistema == True:
        permisos = Permisos.objects.filter(sistema=True)
    else:
        permisos = Permisos.objects.filter(sistema=False)
    print user_logged
    
    if int(user_logged) == 0: 
        proyecto = Proyectos.objects.get(pk=proyecto_id)
        return render_to_response("apps/role_set_permisos_mod_proj.html", {"permisos":permisos, 'rol':rol, 'user_logged':user_logged, 'proyecto':proyecto, 'role_id':role_id}, context_instance=RequestContext(request))
        
        
    return render_to_response("apps/role_set_permisos_mod.html", {"permisos":permisos, "role_id":role_id, "role_descripcion":rol.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
    
           
def asignarpermisosmod(request, user_logged, role_id, proyecto_id):
    """
    Asigna permisos a un rol
    @param request: Http request
    @param role_id: Id de un rol registrado en el sistema
    @return: render a apps/role_modified.html 
    """
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    r = get_object_or_404(Roles, pk=role_id)
    #CONTROLAR!
    lista = request.POST.getlist(u'permisos')
    user = r
    for pr in Permisos_Roles.objects.all():
        if pr.roles_id == user.id:
            Permisos_Roles.objects.filter(pk=pr.id).delete()
            
    for p in lista:
        try:
            permiso = Permisos.objects.get(pk=p)
        except Permisos.DoesNotExist:
            permiso = None
        permrol = Permisos_Roles()
        permrol.roles_id = r.id
        permrol.permisos_id = permiso.id
        permrol.save()

    roles = Roles.objects.filter(sistema=False)
    if int(user_logged) == 0:
        user = request.user
        mispermisos = misPermisos(user.id, proyecto_id)
        return render_to_response("apps/role_admin_project.html", {"roles":roles, 'proyecto':proyecto, 'misPermisos':mispermisos, 'user_logged':user_logged, 'modificado':True}, context_instance=RequestContext(request))
    
    return render_to_response("apps/role_modified.html",{'user_logged':user_logged}, context_instance=RequestContext(request))
    
def inicializarPermisos():
    """
    Inicializa los permisos, poniendo los estados a False
    """
    for p in Permisos.objects.all():
        p.estado = False
        p.save()
        
def roledelete(request, user_logged, role_id):
    """
    Establece el estado de un rol a False
    @param request: Http request
    @param role_id: Id de un rol registrado en el sistema
    @return: render a apps/role_deleted.html
    """
    r = get_object_or_404(Roles, pk=role_id)
    
    r.estado = False
    r.save()
    
    return render_to_response("apps/role_deleted.html",{'user_logged':user_logged}, RequestContext(request))

###################################################################################################################################################

###################################################################################################################################################

class FlowCreateForm(forms.ModelForm):
    class Meta:
        model = Flujos
        fields = ("descripcion",) 
        
class ActivityCreateForm(forms.ModelForm):
    class Meta:
        model = Actividades
        fields = ("descripcion",)
        
def listflowmod(request, user_logged):
    """
    @param request: Http request
    @return: Retorna una lista con todas las plantillas de flujo activas y lo envia al template
    de modificacion de plantilla de flujos
    """
    permisos = misPermisos(user_logged, 0)
    rol_permiso = Users_Roles.objects.get(user_id = user_logged)
    rol = Roles.objects.get(pk=rol_permiso.role_id)
    flujos = Flujos.objects.filter(estado = True, plantilla = True)
    return render_to_response("apps/flow_admin.html",{'misPermisos':permisos, 'user_logged':user_logged, 'rol_id':rol.id, "flujos":flujos})
        
def crearflujo(request, user_logged):
    """
    Crea una plantilla de flujo
    @param request: Http request    
    @return: render a apps/flow_set_activities.html con el id del flujo creado
    """
    error = False
    if request.method == 'POST':
        form = FlowCreateForm(request.POST)
        if form.is_valid():
            form.save()
            try:    
                flow = Flujos.objects.get(descripcion = form.cleaned_data['descripcion'])
            except:
                flow = Flujos.objects.latest('id')
                flow.delete()
                error = True
                return render_to_response('apps/flow_create.html', {'form':form, 'user_logged':user_logged, 'error':error}, context_instance=RequestContext(request))
            
            flow_id = flow.id
            formulario = ActivityCreateForm()
        return render_to_response('apps/flow_set_activities.html', {'formulario':formulario, 'flow_id':flow_id, 'flow_descripcion':flow.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
    else:
        form = FlowCreateForm()
    
    return render_to_response('apps/flow_create.html', {'form':form, 'user_logged':user_logged}, context_instance=RequestContext(request))
    
def setactividades(request, user_logged, flow_id):
    """
    Agrega actividades a una plantilla de flujo
    @param request: Http request    
    @param flow_id: Id de una plantilla de flujo 
    @return: render a apps/flow_created.html
    """
    f = get_object_or_404(Flujos, pk=flow_id)
    if request.method == 'POST':
        form = ActivityCreateForm(request.POST)
        if form.is_valid():
            actv = Actividades()
            actv.flujo_id = f.id
            actv.descripcion = form.cleaned_data['descripcion']
            actv.save()
            
            #form.save()
            if request.POST['submit'] == "Guardar y Agregar otra Actividad":
                formulario = ActivityCreateForm()
                return render_to_response('apps/flow_set_activities.html', {'formulario':formulario, 'flow_id':flow_id, 'flow_descripcion':f.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
            elif request.POST['submit'] == "Guardar y Salir":
                actividades = Actividades.objects.filter(flujo_id = f.id)
                print f.descripcion
                f.tamano = 0
                print f.tamano
                for a in actividades:
                    f.tamano = f.tamano + 3
                f.save()
                return render_to_response('apps/flow_created.html', {'flow_id':flow_id, 'flow_descripcion':f.descripcion, 'user_logged':user_logged}, context_instance = RequestContext(request))
        else:
            return render_to_response('apps/flow_not_valid.html', {"user_logged":user_logged}, context_instance=RequestContext(request))
    else:
        formulario = ActivityCreateForm()
    
    return render_to_response('apps/flow_set_activities.html', {'formulario':formulario, 'flow_id':flow_id, 'flow_descripcion':f.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request)) 



def editarflujos(request, user_logged, flow_id):
    """
    Edita una plantilla de flujo
    @param request: Http request    
    @param flow_id: Id de una plantilla de flujo 
    @return: render a apps/flow_set_activities_mod.html con una lista de actividades y el id del flujo
    """
    flujo = get_object_or_404(Flujos, pk=flow_id)
    
    if request.method == 'POST':
        form = FlowCreateForm(request.POST)
        if form.is_valid():
            flujo.descripcion = form.cleaned_data['descripcion']
            flujo.save()
            #form.save()
            
            actividades = Actividades.objects.filter(flujo_id=flow_id)
            
            #return render_to_response("apps/flow_set_activities_mod.html", {"actividades":actividades, "flow_id":flow_id, 'flow_descripcion':flujo.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
            return listactivitiesmod(request, user_logged, flow_id)
    else:
        form = FlowCreateForm(initial={'descripcion':flujo.descripcion, 'estado':flujo.estado})
    
    
    return render_to_response('apps/flow_modify_form.html', {'form':form, 'flujo':flujo, 'flow_id':flujo.id, 'user_logged':user_logged}, context_instance=RequestContext(request))

def listactivitiesmod(request, user_logged,  flow_id):
    """
    Obtiene la lista de actividades de una plantilla de flujo
    @param request: Http request
    @param flow_id: Id de una plantilla de flujo
    @return: render a apps/flow_set_activities_mod.html con la lista de actividades, el id y la descripcion del flujo
    """
    actividades = Actividades.objects.filter(flujo_id=flow_id)
    flujo = get_object_or_404(Flujos, pk=flow_id)
    #return render_to_response("apps/flow_set_activities_mod.html", {"actividades":actividades, "flow_id":flow_id, 'flow_descripcion':flujo.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
    return render_to_response("apps/flow_set_activities_mod.html", {"actividades":actividades, "flow_id":flow_id, 'flow_descripcion':flujo.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))

def setactividadesmod(request, user_logged, flow_id, actv_id):
    """
    Modifica las actividades de una plantilla de flujo
    @param request: Http request
    @param flow_id: Id de una plantilla de flujo
    @param actv_id: Id de una actividad
    @return: render a apps/flow_activity_modified.html
    """
    f = get_object_or_404(Flujos, pk=flow_id)
    a = get_object_or_404(Actividades, pk=actv_id)
    if request.method == 'POST':
        form = ActivityCreateForm(request.POST)
        if form.is_valid():
            a.descripcion = form.cleaned_data['descripcion']
            a.save()
            return render_to_response("apps/flow_activity_modified.html", {'flow_id':flow_id, 'flow_descripcion':f.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
    else:
        form = ActivityCreateForm(initial={'descripcion':a.descripcion})
    
    return render_to_response('apps/flow_set_activities_mod_form.html', {'form':form, 'flow_id':flow_id, 'actv_id':actv_id, 'user_logged':user_logged}, context_instance=RequestContext(request))


def setactividadesdel(request, user_logged, flow_id, actv_id):
    """
    Establece el estado de una actividad a False
    @param request: Http request
    @param flow_id: Id de una plantilla de flujo
    @param actv_id: Id de una actividad
    @return: render a  apps/flow_activity_eliminated.html  
    """
    flujo = get_object_or_404(Flujos, pk = flow_id)
    a = Actividades.objects.get(pk=actv_id)
    a.estado = False
    a.save()
    return render_to_response("apps/flow_activity_eliminated.html", {"flow_id":flow_id, 'flow_descripcion':flujo.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))

def listflowdel(request):
    """
    @param request: Http request
    @return: Retorna una lista con todas las plantillas de flujo activas y lo envia al template
    de eliminacion de plantilla de flujos
    """
    flujos = Flujos.objects.filter(estado = True, plantilla = True)
    return render_to_response("apps/flow_delete.html", {"flujos":flujos})

def flowdelete(request, user_logged,  flow_id):
    """
    Establece el estado de un flujo a False
    @param request: Http request
    @param flow_id: Id de una plantilla de flujo
    @return: render a  apps/flow_eliminated.html 
    """
    '''
    f = get_object_or_404(Flujos, pk=flow_id)
    f.estado = False
    f.save()
    '''
    eliminarflujo(request, flow_id)
    return render_to_response("apps/flow_eliminated.html",{'user_logged':user_logged}, context_instance=RequestContext(request))

def flowdeleteproj(request, proyecto_id, flujo_id):
    """
    obtiene una lista de flujos a ser eliminados
    @param request:Http
    @param proyecto_id: id del proyecto actual
    @param flujo_id: id del flujo a ser eliminado
    @return: render a project_modificar_listflujo con el proyecto, la lista de flujos, las actividades, y un valor bool que indica si se el rol se ha eliminado
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    flujos = Flujos.objects.filter(proyecto_id = proyecto_id, estado=True)
    actividades = Actividades.objects.filter(plantilla = False , estado=True)
    
    eliminarflujo(request, flujo_id)
    eliminado = True
    return render_to_response("apps/project_modificar_listflujo.html", {"proyecto":proyecto , "flujos":flujos, "actividades":actividades, 'eliminado':eliminado})
    
 
def eliminarflujo(request, flow_id):
    """
    Elimina un flujo
    @param request: Http
    @param flow_id: id del flujo a ser eliminado
    @return: objeto tipo Flujo
    """
    f = get_object_or_404(Flujos, pk=flow_id)
    #f.estado = False
    f.delete()
    return f
###############################creacion de proyecto#################################################################################################

#####################################################################################################################################################

def adminproject(request, user_logged):
    """
    obtiene el usuario logueado y sus permisos
    @param request:Http
    @param user_logged: id del usuario logueado en el sistema
    @return: render a apps/project_admin con la lista de permisos del usuario, su id, y su rol
    """
    permisos = misPermisos(user_logged, 0)
    rol_permiso = Users_Roles.objects.get(user_id = user_logged)
    rol = Roles.objects.get(pk=rol_permiso.role_id)
    return render_to_response('apps/project_admin.html', {'misPermisos':permisos, 'user_logged':user_logged, 'rol_id':rol.id})
    
def verProyectos(request, user_logged):
    proyectoslist = Proyectos.objects.all()
    usuarioslist = User.objects.all()
    equipos = Equipo.objects.all()
    eqlist = []
    equiposlist = []
    
    for e in equipos:
        eqlist.append(e)
        if not se_repite(eqlist, e.usuario_id, e.proyecto_id):
            equiposlist.append(e)

    
    return render_to_response("apps/project_ver_proyectos.html", {'user_logged':user_logged, 'proyectoslist':proyectoslist, 'usuarioslist':usuarioslist, 'equiposlist':equiposlist})

def se_repite(lista, u_id, p_id):
    count = 0
    for l in lista:
        if l.usuario_id == u_id and l.proyecto_id == p_id:
            count = count + 1
        if count > 1:
            return True
    
    return False

def verprojusuario(request, user_logged):
    usuarioslist = User.objects.all()
    proyectoslist = Proyectos.objects.all()
    equipos = Equipo.objects.all()
    equiposlist = []
    eqlist = []
    
    for e in equipos:
        eqlist.append(e)
        if not se_repite(eqlist, e.usuario_id, e.proyecto_id):
            equiposlist.append(e)

    return render_to_response('apps/project_ver_proyectos_users.html', {'user_logged':user_logged, 'equiposlist':equiposlist, 'proyectoslist':proyectoslist, 'usuarioslist':usuarioslist})

def crearProyecto(request, user_logged):
        """
        Crea un proyecto y lo registra en el sistema
        @param request: Http request
        @return:  render a apps/project_add_plantilla.html con un flujo, la lista de actividades del flujo y el id del proyecto creado
        """
        
        if request.method == 'POST':
  
            if  request.POST.get('fechaFin', False) < request.POST.get('fechaInicio', False):
                listUser = User.objects.filter(is_active = True)
                msg = 'La fecha estimada de finalizacion debe ser mayor a la de inicio'
                return render_to_response('apps/project_admin_new.html', {'listuser':listUser, 'user':request.user, 'msg':msg, 'user_logged':user_logged},context_instance=RequestContext(request)) 
            else:
                
                #Creacion de proyecto   
                proyecto = Proyectos()
                proyecto.nombre = request.POST.get('nombre', False)                
                proyecto.descripcion = request.POST.get('descripcion', False)
                proyecto.observaciones = request.POST.get('observaciones', False)
                proyecto.fecha_ini = request.POST.get('fechaInicio', False)
                proyecto.fecha_est_fin = request.POST.get('fechaFin', False)
                proyecto.nro_sprint = 0
                proyecto.save()
                
                #Creacion de equipo
                equipo = Equipo()
                #se obtiene el usuario que se ha escogido
                user1 = User.objects.get(username = request.POST['sm'])
                equipo.usuario = user1
          
                equipo.proyecto = proyecto
                equipo.rol = Roles.objects.get(descripcion = 'Scrum Master')
                equipo.save()
                
                #Se asocia un proyecto con un usuario con el rol cliente
                team = Equipo()
                #se obtiene el usuario que se ha escogido
                user2 = User.objects.get(username = request.POST['cli'])
                team.usuario = user2
          
                team.proyecto = proyecto
                team.rol = Roles.objects.get(descripcion = 'Cliente')
                team.save()
                
                flujo = Flujos.objects.filter(plantilla = True, estado = True)
                actividades = Actividades.objects.filter(plantilla = True)
                
                #Se le envia una notificacion al usuario asignado como Scrum Master
                asunto = 'SGPA-Asignacion a Proyecto'
                msg = 'Su usuario: '+user1.username+', ha sido asignado al proyecto: '+proyecto.nombre+', con el rol de Scrum Master'
                l1 = []
                l1.append(user1)                
                enviarMail(asunto, msg, l1)
                #Se le envia una notificacion al usuario asignado como Cliente
                msg = 'Su usuario: '+user2.username+', ha sido asignado al proyecto: '+proyecto.nombre+', con el rol de Cliente'
                l2 = []
                l2.append(user2)
                enviarMail(asunto, msg, l2)
            
            return render_to_response('apps/project_add_plantilla.html', {'flujo':flujo,'actividades':actividades, 'p_descripcion':proyecto.descripcion, 'idp':proyecto.id, 'user_logged':user_logged},context_instance=RequestContext(request))
            
            
        else:
            
            listUser = User.objects.filter(is_active = True)
            return render_to_response('apps/project_admin_new.html', {'listuser':listUser, 'user':request.user, 'user_logged':user_logged},context_instance=RequestContext(request)) 

            
        


def agregarPlantilla(request, user_logged, proyecto_pk):
    """
    Asigna una plantilla a un proyecto creado
    @param request: Http request
    @return:  render a apps/plantilla_anadida.html
    """
    flujo = Flujos.objects.get(id=request.POST['f'])
    
    copyFlujo = Flujos()
    copyFlujo.descripcion = flujo.descripcion
    copyFlujo.plantilla = False
    copyFlujo.estado = True
    copyFlujo.proyecto_id = proyecto_pk
    copyFlujo.save()                 
    
    actividades = Actividades.objects.filter(flujo_id = request.POST['f'])    
    count = 0
    for actividad in actividades:
        copyActividad = Actividades()             
        copyActividad.descripcion = actividad.descripcion
        copyActividad.estado = True
        copyActividad.plantilla = False
        copyActividad.flujo_id = copyFlujo.id
        copyActividad.save()
        count = count + 3
    
    copyFlujo.tamano = count
    copyFlujo.save()
      
     
    us = Equipo.objects.get(proyecto_id= proyecto_pk, rol_id=3)
    us2 = Equipo.objects.get(proyecto_id= proyecto_pk, rol_id=4)
    
    scrumMaster = User.objects.get(id = us.usuario_id)
    cliente = User.objects.get(id = us2.usuario_id)
    proyecto = Proyectos.objects.get(id = proyecto_pk)
    
    #crearSprints(proyecto_pk)
    mispermisos = misPermisos(request.user.id, proyecto.id)
    return render_to_response('apps/plantilla_anadida.html',{'copyFlujo':copyFlujo,'proyecto':proyecto, 'mispermisos':mispermisos, 'scrum':scrumMaster,'cli':cliente, 'user_logged':user_logged},context_instance=RequestContext(request))

#################################################################################################################################################

#################################################################################################################################################

def listproyectosdelusuario(request, usuario_id):
    """
    Retorna una lista con todos los proyectos del usuario
    
    @param request: Http request
    @param usuario_id: id de un usuario
    @return: render a apps/project_mod.html con la lista de proyectos del usuario, el usuario, sus roles en cada proyecto y su rol de sistema
    """
    #'''Se compara con el registro en la tabla User_Roles'''
    ur = Users_Roles.objects.get(user_id=usuario_id)
    #'''De la tabla de Roles se trae el id del rol del usuario'''
    rolSistema = Roles.objects.get(pk=ur.role_id)
   
    equipos = Equipo.objects.filter(usuario_id=usuario_id)
    proyectos_id = []
    for equipo in equipos:
        esta = False
        for proyecto_id in proyectos_id:
            if proyecto_id == equipo.proyecto_id:
                esta = True
                break
        if esta == False:
            proyectos_id.append(equipo.proyecto_id)
            
    proyectos = []
    for proyecto_id in proyectos_id:
        proyectos.append(Proyectos.objects.get(id = proyecto_id))
    
    rolesProyectos = []
    for proyecto_id in proyectos_id:
        rolesProyecto = Equipo.objects.filter(proyecto_id = proyecto_id, usuario_id = usuario_id)
        roles = []
        for rolProyecto in rolesProyecto:
            rol = Roles.objects.get(id = rolProyecto.rol_id)
            roles.append(rol.descripcion)
        rolesProyectos.append(roles)

    
    return render_to_response("apps/project_mod.html", {"proyectos":proyectos, "usuario":request.user, "roles":rolesProyectos ,"rol_id":rolSistema.id, 'user_id':usuario_id})

def listasigparticipante(request, proyecto_id):
    """
    Lista de usuarios que pueden participar en el proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @return: render a apps/project_asignar_participante.html con la lista de usuarios que pueden ser asignados al proyecto y el proyecto en el cual se encuentra el usuario
    """
    usuarios = []
    proyecto = Proyectos.objects.get(id = proyecto_id)
    equipos = Equipo.objects.filter(proyecto_id = proyecto_id)
    for usuario in User.objects.all():
        seEncuentra = False
        for equipo in equipos:
            if equipo.usuario_id == usuario.id:
                seEncuentra = True
                break
        if seEncuentra == False:
            if usuario.is_active == True:
                yaListado = False
                for u in usuarios:
                    yaListado = False
                    if u.id == usuario.id:
                        yaListado = True
                        break
                if yaListado == False:
                    usuarios.append(usuario)
                
    return render_to_response("apps/project_asignar_participante.html", {"usuarios":usuarios, "proyecto":proyecto})

def listelimparticipante(request, proyecto_id):
    """
    Lista de usuarios que pueden ser eliminados del proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @return: render a apps/project_eliminar_participante.html con la lista de usuarios asignados al proyecto y el proyecto en el cual se encuentra
    """
    usuarios = []
    proyecto = Proyectos.objects.get(id = proyecto_id)
    equipos = Equipo.objects.filter(proyecto_id = proyecto_id)
    for usuario in User.objects.all():
        seEncuentra = False
        for equipo in equipos:
            if equipo.usuario_id == usuario.id and equipo.rol_id !=3:
                seEncuentra = True
                break
        if seEncuentra == True:
            usuarios.append(usuario)

    return render_to_response("apps/project_eliminar_participante.html", {"usuarios":usuarios, "proyecto":proyecto})

def listasigparticipanterol(request, proyecto_id, usuario_id):
    """
    Lista de roles que se pueden asignar a los usuarios
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @param usuario_id: id de un usuario
    @return: render a apps/project_asignar_participante_rol.html con el proyecto donde se encuentra el usuario, el usuario a quien pertenece los roles y los roles del mismo
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    usuario = User.objects.get(id = usuario_id)
    '''
    roles = []
    for rol in Roles.objects.all():
        if rol.estado == True:
            roles.append(rol)
    '''
    roles = Roles.objects.filter(estado = True, sistema = False)
            
    return render_to_response("apps/project_asignar_participante_rol.html", {"proyecto":proyecto, "usuario":usuario, "roles":roles}, context_instance=RequestContext(request))

def accionesproyecto(request, proyecto_id):
    """
    Envia a la pagina desde donde se pueden ejecutar acciones por el proyecto
    
    @param request: Http request 
    @param proyecto_id: id de un proyecto
    @return: render a apps/project_acciones.html si el usuario es Scrum Master junto con el proyecto en el cual se encuentra y el usuario
    @return: render a apps/project_acciones_no_sm.html si el usuario no es Scrum Master junto con el proyecto en el cual se encuentra y el usuario
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    #user_id = request.user
    #urp = Equipo.objects.filter(usuario_id=user_id, rol_id = 3, proyecto_id = proyecto_id)
    #for u in urp:
    mispermisos = misPermisos(request.user.id, proyecto_id)
    #if urp:
        #Si el usuario es Scrum Master en el Proyecto
    uroles = Equipo.objects.filter(proyecto_id = proyecto_id)
    users = []
    roles = []    
    
    for ur in uroles:
        if not is_in_list(users, ur.usuario_id):
            users.append(User.objects.get(pk = ur.usuario_id))
    
    '''
    for ur in uroles:
        listu = Equipo.objects.filter(proyecto_id=proyecto_id, usuario_id=ur.usuario_id)
        if len(listu) > 1:
            listhu.
        else:
            users.append(User.objects.get(pk = ur.usuario_id))
    '''   
    for ur in uroles:
        if not is_in_list(roles, ur.rol_id):
            roles.append(Roles.objects.get(pk = ur.rol_id))
    
    
    #roleslist = Roles.objects.filter(proyecto_id = proyecto_id)
    #roles = []
    

    flujo = Flujos.objects.filter(proyecto_id = proyecto_id, estado=True)
    
    actividades = Actividades.objects.all()
    hus = UserStory.objects.filter(proyecto_id = proyecto_id, estado=True, sprint=proyecto.nro_sprint)
    hu = sorted(hus, key=gethuidsort, reverse=False)
    for hu in hus:
        if hu.f_a_estado != 0 and hu.f_actividad != 0:
            hu.flujo_posicion = ((hu.f_actividad - 1)*3) + hu.f_a_estado
            hu.save()
            
    
    tamanolista = []
    for act in actividades:
        tamanolista.append(act)
        tamanolista.append(act)
        tamanolista.append(act)
        
    user_logged = request.user
    
    
       
    scrum = False
    usereq = Equipo.objects.filter(proyecto_id = proyecto_id, usuario_id=user_logged.id, rol_id = 3)
    if len(usereq):
        scrum = True
    
        
    return render_to_response("apps/project_acciones.html", {"proyecto":proyecto, 'scrum':scrum, 'user_logged':user_logged, "usuario":request.user, "misPermisos":mispermisos, 'equipo':uroles,'users':users, 'roles':roles, 'flujo':flujo, 'actividades':actividades, 'hus':hus, 'tamanolista':tamanolista})

def is_in_list(list, o_id):
    """
    Funcion que controla si un objeto esta o no en una lista
    
    @param list: lista de objetos
    @param o_id: objeto a buscar
    @return: True si el objeto se encuentra, False en otro caso
    """
    for il in list:
        if il.id == o_id:
            return True
    
    return False


def elimparticipante(request, proyecto_id, usuario_id):
    """
    Elimina al usuario del proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @param usuario_id: id de un usuario
    @return: render a apps/project_eliminar_participante_eliminado.html con el proyecto en el cual se encuentra y el usuario
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)  
    Equipo.objects.filter(usuario_id = usuario_id, proyecto_id = proyecto_id).delete()
    user = User.objects.get(id = usuario_id)
    #Se le envia una notificacion al usuario encargado del user story
    asunto = 'SGPA-Desvinculacion de proyecto'
    msg = 'Su usuario: '+user.username+', ha sido desvinculado del proyecto: '+proyecto.nombre
    l = []
    l.append(user)    
    enviarMail(asunto, msg, l)
    
    return render_to_response("apps/project_eliminar_participante_eliminado.html", {"proyecto":proyecto, "usuario":request.user})

def asigparticipanterol(request, proyecto_id, usuario_id):
    """
    Asigna el usuario al proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @param usuario_id: id de un usuario
    @return: render a apps/project_asignar_participante_rol_asignado.html con el proyecto en el cual se encuentra
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    roles = request.POST.getlist(u'roles[]')
    for r in roles:
        try:
            rol = Roles.objects.get(pk=r)
        except:
            rol = None
        equipo = Equipo()
        equipo.usuario_id = usuario_id
        equipo.rol_id = rol.id
        equipo.proyecto_id = proyecto_id
        equipo.save()
    
    return render_to_response('apps/project_asignar_participante_rol_asignado.html', {"proyecto":proyecto} ,context_instance=RequestContext(request))

def listflujosproyectos(request, proyecto_id):
    """
    Lista las plantillas de los flujos disponibles
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @return: render a apps/project_crear_flujo.html con el proyecto en el cual se encuentra, los flujos del proyecto y las actividades de los flujos
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    #flujos = Flujos.objects.filter(estado = True, plantilla = True)
    flujos = getlistaflujos(request, proyecto_id)
        
                    
    actividades = Actividades.objects.filter(plantilla = True)
    
    return render_to_response('apps/project_crear_flujo.html', {"proyecto":proyecto, "flujos":flujos, "actividades":actividades, 'proyecto':proyecto}, context_instance=RequestContext(request))

def getlistaflujos(request, proyecto_id):
    """
    Funcion que captura los flujos disponibles para el proyecto
    
    @param request: Http
    @param proyecto_id: id del proyecto en cuestion
    @return: Lista de flujos
    """
    fproy = Flujos.objects.filter(proyecto_id = proyecto_id)
    ftotal = Flujos.objects.all()
    flujos = []
    existe = False
    for fi in ftotal:
        nombre_flujo = fi.descripcion
        list_flujo_nombre = Flujos.objects.filter(descripcion = nombre_flujo)
        for fj in list_flujo_nombre:
            if fj.proyecto_id == proyecto_id and fj.estado == True:
                existe = True
        if existe == False:
            try:
                flujo_nuevo = Flujos.objects.get(descripcion = nombre_flujo, plantilla = True)
            except Flujos.DoesNotExist:
                flujo_nuevo = None
            
            if flujo_nuevo != None:
                ex = False
                for fk in fproy:
                    if flujo_nuevo.descripcion == fk.descripcion:
                        ex = True
                
                if ex == False:
                    flujos.append(flujo_nuevo)
                    #pass
        existe = False
    
    return flujos
    
def agregarPlantillaProyecto(request, proyecto_id):
    """
    Asigna los nuevos flujos al proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @return: render a apps/project_crear_flujo_creado.html con el proyecto donde se encuentra
    """
    actcount = 0
    proyecto = Proyectos.objects.get(id = proyecto_id)
    flujos_id = request.POST.getlist(u'f[]')
    for flujo_id in flujos_id:
        flujo = Flujos.objects.get(id = flujo_id)
        nuevoFlujo = Flujos()
        nuevoFlujo.descripcion = flujo.descripcion
        nuevoFlujo.plantilla = False
        nuevoFlujo.estado = True
        nuevoFlujo.proyecto_id = proyecto_id
        nuevoFlujo.save()
        actividades = Actividades.objects.filter(flujo_id = flujo_id)
        for actividad in actividades:
            nuevaActividad = Actividades()
            nuevaActividad.descripcion = actividad.descripcion
            nuevaActividad.estado = actividad.estado
            nuevaActividad.plantilla = False
            nuevaActividad.flujo_id = nuevoFlujo.id
            nuevaActividad.save()
            actcount = actcount + 3
        nuevoFlujo.tamano = actcount
        nuevoFlujo.save()
        
    return render_to_response('apps/project_crear_flujo_creado.html', {"proyecto":proyecto}, context_instance=RequestContext(request))

def listflujosproyectosMod(request, proyecto_id):
    """
    lista los flujos del proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @return: render a apps/project_modificar_listflujo.html con el proyecto donde se encuentra, los flujos del proyecto y las actividades de los flujos
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    flujos = Flujos.objects.filter(proyecto_id = proyecto_id, estado = True)
    actividades = Actividades.objects.filter(plantilla = False , estado=True)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    
    return render_to_response("apps/project_modificar_listflujo.html", {"proyecto":proyecto , "flujos":flujos, "actividades":actividades, 'misPermisos':mispermisos})

def flujosproyectosRequestMod(request, proyecto_id, flujo_id, actividad_id):
    """
    obtiene los datos de los flujos del proyecto para presentarlos al usuario, quien puede modificarlos
    si se ha llamado este medotodo por el metodo POST, entonces actualiza los campos que debe actualizar
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @param flujo_id: id de un flujo
    @param actividad_id: id de una actividad
    @return: render a apps/project_modificar_flujo.html con el formulario del flujo seleccionado, las actividades del flujo, el proyecto ene l cual se encuentra y el flujo mismo
    """
    modificado = False
    flujo = get_object_or_404(Flujos, pk=flujo_id)
    if request.method == 'POST':
        if request.POST['cambio'] == "modificar flujo":
            formulario = FlowCreateForm(request.POST)
            if formulario.is_valid():
                flujo.descripcion = formulario.cleaned_data['descripcion']
                #flujo.estado = formulario.cleaned_data['estado']
                flujo.save()
                modificado = True
        elif request.POST['cambio'] == "modificar":
            actividad = Actividades.objects.get(id = actividad_id)
            formulario = ActivityCreateForm(request.POST)
            if formulario.is_valid():
                actividad.descripcion = formulario.cleaned_data['descripcion']
                actividad.save()
        elif request.POST['cambio'] == "eliminar":
            actividad = Actividades.objects.get(id = actividad_id).delete()
            
    proyecto = Proyectos.objects.get(id = proyecto_id)
    formFlujo = FlowCreateForm(initial={'descripcion':flujo.descripcion, 'estado':flujo.estado})
    actividades = Actividades.objects.filter(flujo_id = flujo_id)
        
    return render_to_response('apps/project_modificar_flujo.html', {'formFlujo':formFlujo, "actividades":actividades, "proyecto":proyecto, "flujo":flujo, 'modificado':modificado}, context_instance=RequestContext(request))

def flujosproyectosRequestModAct(request, proyecto_id, flujo_id, actividad_id):
    """
    obtiene los datos de la actividad seleccionada de un flujo en especifico para ser modificado o eliminado
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @param flujo_id: id de un flujo
    @param actividad_id: id de una actividad
    @return: render a apps/project_modificar_flujo_actividad.html con el proyecto en el cual se encuentra el usuario, el flujo del cual se modifica/elimina su actividad, la actividad a ser modificada/eliminada y el formulario de la actividad
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    flujo = Flujos.objects.get(id = flujo_id)
    actividad = Actividades.objects.get(id = actividad_id)
    form = ActivityCreateForm(initial={'descripcion':actividad.descripcion})

    return render_to_response('apps/project_modificar_flujo_actividad.html', {"proyecto":proyecto, "flujo":flujo, "actividad":actividad, "form":form}, context_instance=RequestContext(request) )

def listsprint(request, proyecto_id, sprint):
    """
    obtiene la lista de sprints y sus user stories en un proyecto
    
    @param request: Http
    @param proyecto_id: id del proyecto actual
    @param sprint: nro del sprint en cuestion
    @return: render a project_sprint_backlog_list.html con la lista de sprints, lista de User Stories y el objeto del proyecto
    """
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    sprintlista = Sprint.objects.filter(proyecto_id = proyecto_id)
    hulista = []
    allhu = UserStory.objects.all()
    for hu in allhu:
        if hu.sprint != 0:
            hulista.append(hu)
            
    
    if int(sprint) == 0:
        return render_to_response('apps/project_sprint_backlog_list.html', {'sprintlista':sprintlista, 'hu':hulista, 'proyecto':proyecto})
    else:
        #sprintlista = Sprint.objects.filter(proyecto_id = proyecto_id, nro_sprint = sprint)
        hulista = UserStory.objects.filter(sprint = sprint)
        return render_to_response('apps/project_sprint_backlog_list.html', {'sprintlista':sprintlista, 'hu':hulista, 'proyecto':proyecto})
    
    
def listhu(request, proyecto_id):
    """
    obtiene la lista de User Stories de un proyecto dado, para ser modificados o eliminados
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @return: render a apps/hu_admin.html con el proyecto en el que se encuentra el usuario, y la lista de user stories
    """
    
    mispermisos = misPermisos(request.user.id, proyecto_id)
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    hu = UserStory.objects.filter(proyecto_id = proyecto_id)
    hu_activos = UserStory.objects.filter(proyecto_id = proyecto_id, estado = True, sprint = proyecto.nro_sprint, finalizado = False) 
    hu_plan = UserStory.objects.filter(proyecto_id = proyecto_id, estado = True, finalizado = False)
    hu_planificados = []
    for i in hu_plan:
        if i.sprint > proyecto.nro_sprint:
            hu_planificados.append(i)
    hu_terminados = UserStory.objects.filter(proyecto_id = proyecto_id, estado = True, finalizado = True)
    hu_descartados = UserStory.objects.filter(proyecto_id = proyecto_id, estado = False)
    hu = sorted(hu, key=gethuid, reverse=True)
    hu_no_planificados = UserStory.objects.filter(proyecto_id = proyecto_id, estado = True, sprint = 0)
    
    user_logged = request.user
    print user_logged.id
    
    
       
    scrum = False
    usereq = Equipo.objects.filter(proyecto_id = proyecto_id, usuario_id=user_logged.id, rol_id = 3)
    if len(usereq):
        scrum = True
    
    return render_to_response('apps/hu_admin.html', { 'hu':hu, 'proyecto':proyecto, 'proyecto_descripcion':proyecto.nombre, 'scrum':scrum, 'user_logged':user_logged, 'misPermisos':mispermisos, 'hu_activos':hu_activos, 'hu_planificados':hu_planificados, 'hu_terminados':hu_terminados, 'hu_descartados':hu_descartados, 'hu_noplanificados':hu_no_planificados})

def gethuid(hu):
    """
    Funcion utilizada para ordenar una lista en base a la fecha
    @param hu: Objeto User Story
    @return: la fecha de creacion del User Story
    """
    return hu.fecha_creacion

def gethuidsort(hu):
    """
    Funcion utilizada para ordenar una lista en base al id
    @param hu: Objeto User Story
    @return: la fecha de creacion del User Story
    """
    return hu.id
    
def resumenHu(request, proyecto_id, hu_id):
    """
    funcion utilizada para mostrar el resumen de User Story
    @param request:Http
    @param proyecto_id: id del proyecto del User Story
    @paramm hu_id: id del User Story
    @return: render a apps/hu_resuemn con el id y el nombre del proyecto, y el objeto User Story
    """
    hu = UserStory.objects.get(pk=hu_id)
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    return render_to_response('apps/hu_resumen.html', {'proyecto_id':proyecto_id, 'hu':hu, 'proyecto_nombre':proyecto.nombre})

def listhuflujo(request, proyecto_id, hu_id):
    """
    obtiene la lista de flujos para ser asignados a un user stoty de un proyecto
    
    @param request: Http request
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un User Story
    @return: render a hu_add_flujo.hml con el User Story, su descripcion y su proyecto respectivo, y la lista de flujos a ser seleccionados, como sus actividades
    """
    flujo = Flujos.objects.filter(estado = True, plantilla = True)
    hu = UserStory.objects.get(pk=hu_id)
    actividades = Actividades.objects.all()
    return render_to_response('apps/hu_add_flujo.html', {'proyecto_id':proyecto_id, 'hu_id':hu_id, 'flujo':flujo, 'hu_descripcion':hu.descripcion, 'actividades':actividades}, RequestContext(request))
    

class HuCreateForm(forms.ModelForm):
    """
    formulario de crecion de User Story
    """
    class Meta:
        model = UserStory
        fields = ("descripcion", "codigo", "tiempo_Estimado", "valor_Negocio", "valor_Tecnico")
        
        
def crearHu(request, proyecto_id):
    """
    crea un nuevo User Story
    
    @param request: Http
    @param proyecto_id: id del proyecto en el que se creara el User Story
    @return: render a hu_creado.html con el proyecto en el que se crea el User Story
    @return: render a hu_form_no_valido.html
    @return: render a hu_create.html con el id del proyecto en cuestion, y el formulario de creacion del User Story
    """
    '''
    users = []

    eq = Equipo.objects.filter(proyecto_id = proyecto_id)
    for e in eq:
        users.append(User.objects.get(pk=e.usuario_id))
    '''
    users = []           
    equipos = Equipo.objects.filter(proyecto_id = proyecto_id)
    for equipo in equipos:
        user = User.objects.get(id = equipo.usuario_id)
        se_encuentra = False
        for u in users:
            if u.id == user.id:
                se_encuentra = True
        if se_encuentra == False:
            users.append(user)
            
    flujos = Flujos.objects.filter(proyecto_id = proyecto_id)
    prioridades = Prioridad.objects.all()
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    if request.method == 'POST':
        form = HuCreateForm(request.POST)
       
        #if form.is_valid():
        #form.save()
        #hu = UserStory.objects.get(pk=form.cleaned_data['id'])
        #hu = UserStory.objects.get(codigo  = form.cleaned_data['codigo'])
        hu = UserStory()
        #hu = UserStory.objects.latest('id')
        hu.nombre = request.POST['nombre']
        hu.codigo = request.POST['codigo']
        hu.descripcion = request.POST['descripcion']
        hu.tiempo_Estimado = request.POST['tiempoestimado']
        hu.valor_Negocio = request.POST['valornegocio']
        hu.valor_Tecnico = request.POST['valortecnico']
        hu.estado_scrum_id = Estados_Scrum.objects.get(pk=3)
        hu.proyecto_id = proyecto_id
        hu.fecha_creacion = time.strftime("%Y-%m-%d")
        #user = User.objects.get(username = request.POST['us']) 
        #hu.usuario_Asignado =  user.id
        #flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
        #oflujo = flujolist.get(descripcion = request.POST['flujo'])
        #hu.flujo = oflujo.id
        prioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
        hu.prioridad = prioridad
        #hu.notas = request.POST.get('notas', False)
        hu.tiempo_Real = 0
        hu.estado_scrum_id = 3
        hu.save()
        
       
        
        #Se le envia una notificacion al usuario encargado del user story
        #asunto = 'SGPA-Asignacion a User Story'
        #msg = 'Su usuario: '+user.username+', ha sido asignado como el responsable del user story: '+ hu.descripcion+ ', del proyecto: '+proyecto.nombre
        #l = []
        #l.append(user)
        
        #enviarMail(asunto, msg, l)
        return render_to_response('apps/hu_creado.html',{"proyecto_id":proyecto_id},  context_instance = RequestContext(request))
        #else:
            #return render_to_response('apps/hu_form_no_valido.html', context_instance = RequestContext(request))
    else:        
        form = HuCreateForm()
        
    return render_to_response('apps/hu_create.html', {"form":form, 'misPermisos':mispermisos, 'proyecto':proyecto, 'users':users, 'flujos':flujos, 'prioridades':prioridades}, context_instance = RequestContext(request))

def fileAdjunto(request, proyecto_id, hu_id):
    """
    Adjunta un archivo a un user story
    
    @param request: Http
    @param proyecto_id: id del proyecto en el que se creara el User Story
    @param hu_id: id del user story al que se le adjuntara el archivo 
    @return: render a hu_fileManager.html 
    """    
    mispermisos = misPermisos(request.user.id, proyecto_id)
    hu = UserStory.objects.get(pk=hu_id)
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    lista = archivoAdjunto.objects.filter(hu_id = hu_id,actual = True) 
    msg = ""
    if request.method == 'POST':
     
        hu = UserStory.objects.get(id = hu_id)
        file = request.FILES['file']
        print file.size
        if file.size <= 10485760:
            count = archivoAdjunto.objects.filter(filename = file.name, hu = hu_id).count()
            
            print "count: " 
            print count
            if count >0:
                oldAdjunto = archivoAdjunto.objects.get(filename = file.name, hu = hu_id, actual = True)
                oldAdjunto.actual = False;
                
                adjunto = archivoAdjunto()
                data = file.read()
                archivoAdjunto.set_data(adjunto, data)
       
                adjunto.hu=hu
                adjunto.size = file.size
                adjunto.filename = file.name
                
                adjunto.version = oldAdjunto.version +1
                adjunto.save()  
                oldAdjunto.save()
        
                return render_to_response('apps/hu_fileManager.html', {"msg":msg,"lista":lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))
            else:
                adjunto = archivoAdjunto()
                data = file.read()
                archivoAdjunto.set_data(adjunto, data)
       
                adjunto.hu=hu
                adjunto.size = file.size
                adjunto.filename = file.name
                
                adjunto.save()  
        
                return render_to_response('apps/hu_fileManager.html', {"msg":msg,"lista":lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))
        else:
            msg = "Archivo sobrepaso 10 MB"
        return render_to_response('apps/hu_fileManager.html', {"msg":msg,"lista":lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))

    
    
    return render_to_response('apps/hu_fileManager.html', {"msg":msg,"lista":lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))

def notasHu(request, proyecto_id, hu_id):
    
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    hu = UserStory.objects.get(pk=hu_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    notas = Notas.objects.filter(hu = hu_id)
    
    return render_to_response('apps/hu_notas.html', {'proyecto':proyecto, 'hu':hu, 'notas':notas, 'misPermisos':mispermisos}, context_instance=RequestContext(request))
        
def agregarNotaHu(request, proyecto_id, hu_id):
    
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    hu = UserStory.objects.get(pk=hu_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    notas = Notas.objects.filter(hu = hu_id)
    guardado = False
    if request.method == 'POST':
        nota = Notas()
        nota.descripcion = request.POST['descripcion']
        nota.fechahora = time.strftime("%Y-%m-%d %H:%M")
        nota.user = request.user
        nota.hu = hu
        nota.save()
        notificarNota(proyecto_id,hu_id,nota.descripcion)
        guardado = True
        return render_to_response('apps/hu_notas.html', {'proyecto':proyecto, 'hu':hu, 'misPermisos':mispermisos, 'guardado':guardado, 'notas':notas}, context_instance=RequestContext(request))
    
    return render_to_response('apps/hu_asignar_notas.html', {'proyecto':proyecto, 'hu':hu, 'misPermisos':mispermisos}, context_instance=RequestContext(request))
        
    
def send_file(request,f_id):
    """
    Prepara un archivo adjunto de un user story para su descarga
    
    @param request: HttpRequest
    @param f_id: id del archivo que se desea descargar
    @return response : El archivo para su descarga                                         
    """

    archivo = archivoAdjunto.objects.get(id = f_id)
    data = archivoAdjunto.get_data(archivo)
    file_content = data
    filename = archivo.filename
    
    response = HttpResponse(file_content, content_type='text/plain')
    response['Content-Disposition'] = 'inline; filename=%s'%filename
    
    return response
    
   

def delete_file(request, proyecto_id, hu_id, f_id):
    """
    Elimina un archivo adjunto de un user story
    
    @param request: HttpRequest
    @param proyecto_id: id del proyecto del User Story
    @param hu_id: id del user story donde al que pertenece el archivo 
    @param f_id: id del archivo
    @return HttpResponse a fileAdjunto()
    """
    adjunto = archivoAdjunto.objects.get(id = f_id)
    
    if adjunto.version > 1:
        
        if archivoAdjunto.objects.filter(hu = hu_id, version = adjunto.version -1, filename = adjunto.filename).exists():
            
            adjunto2 = archivoAdjunto.objects.get(hu = hu_id, version = adjunto.version -1, filename = adjunto.filename)
            adjunto2.actual = True
            adjunto2.save()
        
    adjunto.delete()
    
    return HttpResponse(fileAdjunto(request, proyecto_id, hu_id))

def versionesAdjunto(request, proyecto_id, hu_id):
    """
    Retorna una lista de las versiones de los archivos adjuntos
    
    @param request: Http
    @param proyecto_id: id del proyecto en el que se creara el User Story
    @param hu_id: id del user story al que se le adjuntara el archivo 
    @return: render a hu_fileManager_verions.html 
    """    
    mispermisos = misPermisos(request.user.id, proyecto_id)
    hu = UserStory.objects.get(pk=hu_id)
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    lista = archivoAdjunto.objects.filter(hu_id = hu_id,actual = False) 
   
    

    
    
    return render_to_response('apps/hu_fileManager_versions.html', {'lista':lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))
    
def editarHu(request, proyecto_id, hu_id):
    """
    editar un User Story existente
    
    @param request: HttpRequest
    @param proyecto_id: id del proyecto donde se encuentra el User Story a editar
    @param hu_id: id del User Story a editar
    @return: render a hu_modificado.html con el id del proyecto en el que se encuentra el user story
    @return: render a hu_form_no_valido.html 
    @return: hu_modify_fields.html con el id y la descripcion del User Story, el id del proyecto donde se encuentra y el formulario de edicion
    """

    proyecto = Proyectos.objects.get(pk = proyecto_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    hu = get_object_or_404(UserStory, pk=hu_id)
    huv = UserStoryVersiones()
    userasig = False
    try:
        if hu.usuario_Asignado == request.user.id:
            userasig = True
    except:
        userasig = False
    users = []           
    equipos = Equipo.objects.filter(proyecto_id = proyecto_id)
    for equipo in equipos:
        user = User.objects.get(id = equipo.usuario_id)
        se_encuentra = False
        for u in users:
            if u.id == user.id:
                se_encuentra = True
        if se_encuentra == False:
                users.append(user)
    flujos = Flujos.objects.filter(proyecto_id = proyecto_id)
    prioridades = Prioridad.objects.all()
    user_logged = User.objects.get(username = request.user)
    if request.method == 'POST':
        form = HuCreateForm(request.POST)
        #if form.is_valid():
        #form.save()
        copiarHU(hu, huv, user_logged)
        oldnameHU = hu.descripcion
        #hu = UserStory.objects.latest('id')
        hu.nombre = request.POST['nombre']
        hu.codigo = request.POST['codigo']
        hu.descripcion = request.POST['descripcion']
        hu.tiempo_Estimado = request.POST['tiempoestimado']
        hu.valor_Negocio = request.POST['valornegocio']
        hu.valor_Tecnico = request.POST['valortecnico']
        hu.proyecto_id = proyecto_id
        
        #llamada a funcion que notifica a los responsables, la modificacion del hu
        notificarModificacionHU(hu_id,proyecto_id)
        
        
        try:
            user = User.objects.get(username = request.POST['us'])
        except: 
            user = None
        oldUser = hu.usuario_Asignado
        try:
            hu.usuario_Asignado =  user.id
        except:
            hu.usuario_Asignado = None
        

        '''
        try:
            flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
            oflujo = flujolist.get(descripcion = request.POST['flujo'])
        except:
            flujolist = []
        
        
        
        try:
            hu.flujo = oflujo.id
        except:
            hu.flujo = None
        '''    
        prioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
        hu.prioridad = prioridad
        hu.fecha_modificacion = time.strftime("%Y-%m-%d")
        #hu.notas = request.POST.get('notas', False)
        hu.save()
        '''
        #se envian notificaciones si se ha cambiado de responsable del user story
        if oldUser != hu.usuario_Asignado:
            #se obtiene el usuariio que ha sido desvinculado
            user2 = User.objects.get(id = oldUser) 
            #Se le envia una notificacion al usuario encargado del user story
            send_mail('SGPA-Asignacion a User Story',
                   'Su usuario: '+user.username+', ha sido asignado como el responsable del user story: '+ hu.descripcion+ ' del proyecto: '+proyecto.nombre,
                   'noreply.sgpa@gmail.com',
                    [user.email], 
                    fail_silently=False)
            #Se le envia una notificacion al usuario desvinculado del user story
            send_mail('SGPA-Desvinculacion de User Story',
                   'Su usuario: '+user2.username+', ha sido desvinculado del user story: '+ hu.descripcion+ ' del proyecto: '+proyecto.nombre,
                   'noreply.sgpa@gmail.com',
                    [user2.email], 
                    fail_silently=False)
        
        else: 
            #si no se cambio de responsable, se le notifica que el user story experimento cambios
                send_mail('SGPA-Modificacion de User Story',
                   'El User Story: '+oldnameHU+' del proyecto: '+proyecto.nombre+', ha experimentado modificaciones ',
                   'noreply.sgpa@gmail.com',
                    [user.email], 
                    fail_silently=False)  
        '''
        return render_to_response('apps/hu_modificado.html',{"proyecto_id":proyecto_id, 'hu_id':hu_id, 'hu':hu},  context_instance = RequestContext(request))
    #else:
        #return render_to_response('apps/hu_form_no_valido.html', context_instance = RequestContext(request))
    else:        
        form = HuCreateForm(initial={'descripcion':hu.descripcion, 'codigo':hu.codigo, 'tiempo_Estimado':hu.tiempo_Estimado, 'valor_Tecnico':hu.valor_Tecnico, 'valor_Negocio':hu.valor_Negocio})

    return render_to_response('apps/hu_modify_fields.html', {"form":form, "proyecto_id":proyecto_id, "hu_id":hu_id, "hu":hu, 'misPermisos':mispermisos, 'users':users, 'flujos':flujos, 'proyecto_nombre':proyecto.nombre, 'proyecto':proyecto, 'prioridades':prioridades, 'userasig':userasig}, context_instance = RequestContext(request))

def registroHu(request, proyecto_id, hu_id):
    """
    Funcion que muestra el registro de actividades de un User Story
    
    @param request:Http
    @param proyecto_id: id del proyecto del User Story
    @param hu_id: id del User Story
    @return: render a apps/hu_registro.html con el la lista de registros del User Story, el objeto User Story, y el proyecto
    """
    hu = UserStory.objects.get(pk=hu_id)
    hu_reg = UserStoryRegistro.objects.filter(idr = hu.id)
    
    hu_reg = sorted(hu_reg, key=gethudate, reverse=True)
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    
    return render_to_response('apps/hu_registro.html', {'hu_reg':hu_reg, 'hu':hu, 'proyecto':proyecto, 'misPermisos':mispermisos}, context_instance=RequestContext(request))

    
def gethudate(hu):
    """
    Funcion utilizada para ordenar una lista de User Stories en base a la fecha de modificacion
    @param hu: objeto User Story
    @return: la fecha de modificacion del User Story
    """
    return hu.fechahora

def crearregistroHu(request, proyecto_id, hu_id):
    """
    obtiene un User Story, y guarda sus horas consumidas y una descripcion
    
    @param request: Http
    @param proyecto_id: id del proyecto del User Story
    @param hu_id: id del User Story
    @return: render a hu_registro.html con el User Story, el registro del User Story, el proyecto, y un boolenao que indica si el registro ha sido guardado
    @return: render a hu_regisro_nuevo.html con el User Story, el proyecto, y un boolenao que indica si el registro ha sido guardado
    """
    hu = UserStory.objects.get(pk=hu_id)
    user = request.user
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    guardado = False
    if request.method == 'POST':
        hu_reg = UserStoryRegistro()
        hu_reg.idr = hu.id
        copiarHU(hu, hu_reg, user)
        hu_reg.descripcion_tarea = request.POST.get('descripcion_tarea', False)
        hu_reg.tiempo_Real = request.POST.get('tiempo_real', False)
        hu_reg.save()
        guardado = True
        #Asignacion de horas a los dias del sprint
        respuesta = horas(hu_reg, hu_id)
        #aca le tengo que llamar a la notificacion <selm>
        notificarRegistroTrabajo(hu_id, proyecto_id)
        #"respuesta" se puede manejar como sea necesario
        #termina asignacion de horas a los dias del sprint
        hu_reg = UserStoryRegistro.objects.filter(idr = hu.id)
        return render_to_response('apps/hu_registro.html', {'hu':hu, 'proyecto':proyecto, 'guardado':guardado, 'hu_reg':hu_reg}, context_instance=RequestContext(request))
    
    return render_to_response('apps/hu_registro_nuevo.html', {'hu':hu, 'proyecto':proyecto, 'guardado':guardado}, context_instance=RequestContext(request))

def verregistroHu(request, proyecto_id, hu_id):
    """
    Muestra los campos del registro de la actividad
    @param request: Http
    @param proyecto_id: id del proyecto actual
    @param hu_id: id del Registro del User Story
    """
    hu_reg = UserStoryRegistro.objects.get(pk=hu_id)
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    flujo = Flujos.objects.get(pk=hu_reg.flujo)
    actividad = getActividadHu(hu_reg)
    if actividad == None:
        act = "No planificado"
    else:
        act = actividad.descripcion
        
    estado = getEstadoHu(hu_reg)
    if estado == None:
        est = "No planificado"
    else:
        est = estado.descripcion
    
    return render_to_response('apps/hu_registro_mostrar.html', {'hu_reg':hu_reg, 'proyecto':proyecto, 'actividad':act, 'estado':est, 'flujo':flujo.descripcion})

def getActividadHu(hu):
    """
    Funcion que retorna la Actividad del User Story
    @param hu: objeto User Story
    @return: la actividad del User Story
    """
    actividad = None
    actividadeslist = Actividades.objects.filter(flujo_id = hu.flujo)
    count = 0
    for act in actividadeslist:
        count = count + 1
        if count == hu.f_actividad:
            actividad = Actividades.objects.get(pk = act.id)
            
    return actividad

def getEstadoHu(hu):
    """
    Funcion que retorna el estado del User Story
    @param hu: objeto User Story
    @return: el estado del User Story
    
    """
    estado = None
    count = 0
    estadoslist = Estados.objects.all()
    for est in estadoslist:
        count = count + 1
        if count == hu.f_a_estado:
            estado = Estados.objects.get(pk = est.id)
         
    return estado

def volverVersionHU(request, proyecto_id, hu_id, huv_id):
    """
    Funcion que retorna un User Story a una version anterior
    
    @param request: Http
    @param proyecto_id: Id del proyecto actual
    @param hu_id: id de la version actual del User Story
    @param huv_id: id de una version anterior del User Story
    @return: render a hu_list_versiones_cambios.html con el id del proyecto, el User Story, su version User Story, y el objeto del Proyecto
    """
    hu = UserStory.objects.get(pk=hu_id)
    huv = UserStoryVersiones()
    
    user = request.user
    
    mispermisos = misPermisos(request.user.id, 0)
    print user.id
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    #Se crea una nueva version
    copiarHU(hu, huv, user)
    
    huv = UserStoryVersiones.objects.get(pk=huv_id)
    #Se copia la sobre la version actual
    volverHU(hu, huv)
    
    return render_to_response('apps/hu_list_versiones_cambios.html', {'proyecto_id':proyecto_id, 'hu':hu, 'huv':huv, 'proyecto':proyecto, 'misPermisos':mispermisos})
    
def volverHU(hu, huv):
    """
    Funcion que copia todos los elementos de una version al User Story actual
    
    @param hu: objeto User Story con la version actual
    @param huv: objeto User Story con version anterior
    """
    
    hu.nombre = huv.nombre
    hu.descripcion = huv.descripcion
    hu.codigo = huv.codigo
    hu.valor_Negocio = huv.valor_Negocio
    hu.valor_Tecnico = huv.valor_Tecnico
    hu.prioridad = huv.prioridad
    hu.tiempo_Estimado = huv.tiempo_Estimado
    hu.tiempo_Real = huv.tiempo_Real
    #No puede volver al sprint anterior
    hu.sprint = huv.sprint
    hu.usuario_Asignado = huv.usuario_Asignado
    #hu.flujo
    #hu.proyecto
    hu.estado = huv.estado
    #hu.fecha_creacion = huv.fecha_creacion
    #hu.fecha_inicio = huv.fecha_inicio
    hu.fecha_modificacion = time.strftime("%Y-%m-%d")
    hu.f_actividad = huv.f_actividad
    hu.f_a_estado = huv.f_a_estado
    hu.flujo_posicion = huv.flujo_posicion
    hu.finalizado = huv.finalizado
    hu.estado_scrum_id = huv.estado_scrum_id
    hu.motivo_cancelacion = huv.motivo_cancelacion
    
    hu.save()

def copiarHU(hu, huv, user):
    """
    Funcion que hace una copia de todos los campos de un User Story a otro
    
    @param hu: objeto User Story a copiar
    @param huv: objeto User Story de destino
    @param user: objeto del Usuario que realiza una modificacion en el HU
    """
    listhu = UserStoryVersiones.objects.filter(idv=hu.id)
    cantv = listhu.count()
    huv.idv = hu.id
    huv.version = cantv + 1    
    huv.descripcion = hu.descripcion
    huv.nombre = hu.nombre
    huv.codigo = hu.codigo
    huv.valor_Negocio = hu.valor_Negocio
    huv.valor_Tecnico = hu.valor_Tecnico
    huv.tiempo_Real = hu.tiempo_Real
    huv.flujo = hu.flujo
    huv.proyecto = hu.proyecto
    huv.tiempo_Estimado = hu.tiempo_Estimado
    huv.usuario_Asignado = hu.usuario_Asignado
    huv.sprint = hu.sprint
    huv.estado = hu.estado
    huv.prioridad = hu.prioridad
    huv.fechahora = time.strftime("%Y-%m-%d %H:%M")
    #huv.notas = hu.notas
    huv.usercambio = user
    huv.f_actividad = hu.f_actividad
    huv.f_a_estado = hu.f_a_estado
    huv.flujo_posicion = hu.flujo_posicion
    huv.estado_scrum_id = hu.estado_scrum_id
    huv.finalizado = hu.finalizado
    huv.motivo_cancelacion = hu.motivo_cancelacion
    huv.save()

def listhuversiones(request, proyecto_id, hu_id):
    """
    Funcion que retorna la lista de versiones de un determinado User Story
    
    @param request: Http
    @param proyecto_id: id del Proyecto en el que se encuentra el User Story
    @param hu_id: id del User Story en cuestion
    @return: render a hu_list_versiones.html, con el id del User Story, su lista de versiones, y el id del proyecto al que corresponde
    """
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    hu = UserStory.objects.get(pk = hu_id)
    huversiones = UserStoryVersiones.objects.filter(idv = hu_id)
    user_logged = request.user
    mispermisos = misPermisos(request.user.id, proyecto_id)
    return render_to_response('apps/hu_list_versiones.html', {'proyecto_id':proyecto_id, 'misPermisos':mispermisos, 'hu_id':hu_id,'hu':hu, 'hu_versiones':huversiones, 'user_logged':user_logged, 'proyecto':proyecto})
    
def huvcambios(request, proyecto_id, hu_id, huv_id):
    """
    obtiene los atributos de una version de un User Story
    @param request: Http
    @param proyecto_id: id del proyecto del User Story
    @param hu_id: id del User Story
    @param huv_id: id de la version del User Story
    @return: render a hu_list_versiones_cambios.html con el id del proyecto, el objeto User Story, y su version
    """
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    huv = UserStoryVersiones.objects.get(pk=huv_id)
    hu = UserStory.objects.get(pk=hu_id)
    mispermisos = misPermisos(request.user.id, proyecto_id)
    return render_to_response('apps/hu_list_versiones_cambios.html', {'proyecto_id':proyecto_id, 'hu':hu, 'huv':huv, 'proyecto':proyecto, 'misPermisos':mispermisos})

def modificarHu(request, proyecto_id, hu_id):
    """
    obtiene los atributos del User Story a ser modificado
    @param request: Http
    @param proyecto_id: id del proyecto donde se encuentra el User Story
    @param hu_id: id del User Story a ser modificado
    @return: render a hu_modify.html con el id y la descripcion del User Story, y el id del proyecto donde se encuentra
    """
    hu = UserStory.objects.get(pk=hu_id)
    hu_descripcion = hu.descripcion
    return render_to_response('apps/hu_modify.html', {'proyecto_id':proyecto_id, 'hu_id':hu_id, 'hu_descripcion':hu_descripcion})

def setEstadoHu(request, proyecto_id, hu_id):
    """
    Cambia el estado de un User Story
    
    @param request: Http
    @param proyecto_id: id del proyecto del User Story
    @param hu_id: id del User Story
    @param actividades: lista de actividades en el flujo
    @param estados: lista de estados en las actividades
    @return: render a apps/hu_set_estado con el id del proyecto, y del User Story
    """
    proyecto = get_object_or_404(Proyectos, pk = proyecto_id)
    hu = get_object_or_404(UserStory, pk = hu_id)
    flujo = Flujos.objects.get(pk = hu.flujo)
    actividadeslist = Actividades.objects.filter(flujo_id = hu.flujo)
    actividades = []
    count = 0
    for act in actividadeslist:
        if count<=hu.f_actividad:
            actividades.append(act)
        count = count + 1
        
    estadoslist = Estados.objects.all()
    estados = []
    count = 0
    for est in estadoslist:
        if count<=hu.f_a_estado:
            estados.append(est)
        count = count + 1
        
    mispermisos = misPermisos(request.user.id, proyecto_id)
    modificado = False
    ordenact = 0
    if request.method == 'POST':
        #actlist = Actividades.objects.filter(descripcion = request.POST['act'], flujo_id = hu.flujo)
        
        actividadeslist = Actividades.objects.filter(flujo_id = hu.flujo)
        count = 0
        ordenact = 0
        for a in actividadeslist:
            count = count + 1
            if a.descripcion == request.POST['act']:
                ordenact = count
                break
                
        hu.f_actividad = ordenact
        #hu.f_actividad = actlist.get(descripcion = request.POST['act']).id
        
        hu.f_a_estado = Estados.objects.get(descripcion = request.POST['est']).id
        hu.save()
        modificado = True
        return render_to_response('apps/hu_set_estado.html', {'proyecto':proyecto, 'hu':hu, 'actividades':actividades, 'estados':estados, 'flujo_descripcion':flujo.descripcion, 'misPermisos':mispermisos, 'modificado':modificado}, context_instance = RequestContext(request))
    
    #return render_to_response('apps/hu_modify_fields.html', {"form":form, "proyecto_id":proyecto_id, "hu_id":hu_id, "hu_descripcion":hu.descripcion, 'misPermisos':mispermisos, 'users':users, 'flujos':flujos, 'proyecto_nombre':proyecto.nombre, 'prioridades':prioridades, 'hu':hu}, context_instance = RequestContext(request))
    return render_to_response('apps/hu_set_estado.html', {'proyecto':proyecto, 'hu':hu, 'actividades':actividades, 'estados':estados, 'flujo_descripcion':flujo.descripcion, 'misPermisos':mispermisos}, context_instance = RequestContext(request))

def userToHU(request, proyecto_id, hu_id):
    """
    Asignar un usuario a un user story. El usuario debe pertenecer al mismo proyecto que el user story
    @param request: Http
    @param proyecto_id: id del proyecto donde se encuentra el User Story
    @param hu_id: id del User Story a ser modificado
    @return: render a hu_modificado.html con el id y el id del User Story
    """
    huv = UserStoryVersiones()
    user_logged = User.objects.get(username = request.user)
    permisos = misPermisos(user_logged.id, proyecto_id)
    hu = UserStory.objects.get(id = hu_id)
    
    idusers = Equipo.objects.filter(proyecto_id = proyecto_id)
    
    users = []
    
    for us in idusers:
        users.append(User.objects.get(id = us.usuario_id))
        hu = UserStory.objects.get(id = hu_id)
    
    if request.method == 'POST': 
        user_logged = User.objects.get(descripcion = request.user)
        copiarHU(hu, huv, user_logged)       
        print(request.POST['us'])
        user = User.objects.get(username = request.POST['us']) 
        print (user.id) 
        hu.usuario_Asignado =  user.id
        hu.save()
        
        return render_to_response('apps/hu_modificado.html', {'proyecto_id':proyecto_id, 'hu_id':hu.id})
   
    
    return render_to_response('apps/hu_modify_asigUser.html', {'users':users, 'proyecto_id':proyecto_id, 'hu_id': hu_id, 'hu_descripcion':hu.descripcion, 'permisos':permisos},context_instance = RequestContext(request))


def verCliente(request, proyecto_id):
    """
    Permite visualizar los clientes de un proyecto
    @param request: Http
    @param proyecto_id: id del proyecto donde se encuentra el usuario
    @return: render a project_verCliente.html con la lista de clientes(users), la descripcion del proyecto y su id
    """
    team = Equipo.objects.filter(proyecto_id = proyecto_id, rol_id = 4)
    users = []
    for t in team:
        users.append(User.objects.get(id = t.usuario_id))
    proyecto = Proyectos.objects.get(id = proyecto_id, )
    mispermisos = misPermisos(request.user.id, proyecto_id)
    
    return render_to_response('apps/project_verCliente.html', {'users':users, 'misPermisos':mispermisos, 'proyecto':proyecto,'proyecto_id':proyecto_id},context_instance = RequestContext(request))

    
def verUser(request, proyecto_id, user_id):
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    user = User.objects.get(pk=user_id)
    return render_to_response('apps/project_user_info.html', {'proyecto':proyecto, 'user':user})

def eliminarHu(request, proyecto_id, hu_id):
    """
    cambia el estado de un User Story a inactivo
    @param request: Http
    @param proyecto_id: el id del proyecto donde se encuentra el User Story
    @param hu_id: el id del User Story a ser eliminado
    @return: render a hu_deleted.html con el id del proyecto del User Story
    """
    huv=UserStoryVersiones()
    hu = get_object_or_404(UserStory, pk=hu_id)
    hu.estado = False
    hu.estado_scrum = Estados_Scrum.objects.get(pk=6)
    user_logged = User.objects.get(username = request.user)
    copiarHU(hu, huv, user_logged)
    hu.save()
    return render_to_response('apps/hu_deleted.html',{'proyecto_id':proyecto_id}, RequestContext(request))

def asignarflujoHu(request, proyecto_id, hu_id):
    """
    asigna el User Story a un flujo
    @param request: Http
    @param proyecto_id: id del proyecto donde se encuentra el User Story
    @param hu_id: id del User Story a ser asignado a un flujo
    @return: render a hu_flow.html con la descripcion del User Story y el id del proyecto
    """
    huv=UserStoryVersiones()
    hu = get_object_or_404(UserStory, pk = hu_id)
    if request.POST:   
        user_logged = User.objects.get(descripcion = request.user)
        copiarHU(hu, huv, user_logged)
        flujo = Flujos.objects.get(pk = request.POST['f'])
        hu.flujo = flujo.id
        hu.save()
        return render_to_response('apps/hu_flow_set.html', {'hu_descripcion':hu.descripcion, 'proyecto_id':proyecto_id}, context_instance = RequestContext(request))

class misPermisosClass():
    """
    disponibilidad de permisos del usuario
    """
    "Crear Usuario"
    CU = False
    "Modificar Usuario"
    MU = False
    "Eliminar Usuario"
    EU = False
    "Crear Proyecto"
    CP = False
    "Modificar Proyecto"
    MP = False
    "Asignar Participantes a Proyecto"
    APP = False
    "Eliminar Participantes de Proyecto"
    EPP = False
    "Crear User Stories"
    CUS = False
    "Modificar User Stories"
    MUS = False
    "Eliminar User Stories"
    EUS = False
    "Crear Plantilla de Flujos"
    CPF = False
    "Modificar Plantilla de Flujos"
    MPF = False
    "Eliminar Plantilla de Flujos"
    EPF = False
    "Planificar Sprints"
    PS = False
    "Visualizar Proyectos"
    VP = False
    "Crear Roles"
    CR = False
    "Modificar Roles"
    MR = False
    "Eliminar Roles"
    ER = False

def misPermisos(usuario_id, proyecto_id):
    """
    retorna la lista de permisos donde se indica con que permisos cuenta el ususario
    
    @param usuario_id: id de un ususario
    @param proyecto_id: id de un proyecto; vale 0 si el usuario no se encuentra en ningun proyecto
    @return: retorna una lista de permisos
    """
    user = User.objects.get(id = usuario_id)
    roles_usuario = Users_Roles.objects.filter(user_id = user.id)
    roles = []
    for rol_usuario in roles_usuario:
        roles.append(Roles.objects.get(id = rol_usuario.role_id))
    if proyecto_id != 0:
        #Se quitara cuando los roles de sistema y los roles de proyecto esten vien separados
        roles = []
        roles_proyectos = Equipo.objects.filter(usuario_id = user.id, proyecto_id = proyecto_id)
        for rol_proyecto in roles_proyectos:
            roles.append(Roles.objects.get(id = rol_proyecto.rol_id))
    misPermisos = misPermisosClass()
    for rol in roles:
        permisos_rol = Permisos_Roles.objects.filter(roles_id = rol.id)
        for permiso_rol in permisos_rol:
            permiso = Permisos.objects.get(id = permiso_rol.permisos_id)
            if permiso.tag=="CU":
                misPermisos.CU = True
            elif permiso.tag=="MU":
                misPermisos.MU = True
            elif permiso.tag=="EU":
                misPermisos.EU = True
            elif permiso.tag=="CP":
                misPermisos.CP = True
            elif permiso.tag=="MP":
                misPermisos.MP = True
            elif permiso.tag=="APP":
                misPermisos.APP = True
            elif permiso.tag=="EPP":
                misPermisos.EPP = True
            elif permiso.tag=="CUS":
                misPermisos.CUS = True
            elif permiso.tag=="MUS":
                misPermisos.MUS = True
            elif permiso.tag=="EUS":
                misPermisos.EUS = True
            elif permiso.tag=="CPF":
                misPermisos.CPF = True
            elif permiso.tag=="MPF":
                misPermisos.MPF = True
            elif permiso.tag=="EPF":
                misPermisos.EPF = True
            elif permiso.tag=="PS":
                misPermisos.PS = True
            elif permiso.tag=="VP":
                misPermisos.VP = True
            elif permiso.tag=="CR":
                misPermisos.CR = True
            elif permiso.tag=="MR":
                misPermisos.MR = True
            elif permiso.tag=="ER":
                misPermisos.ER = True
            elif permiso.tag=="CRP":
                misPermisos.CRP = True
            elif permiso.tag=="MRP":
                misPermisos.MRP = True
            elif permiso.tag=="ERP":
                misPermisos.ERP = True
            elif permiso.tag=="AFP":
                misPermisos.AFP = True
            elif permiso.tag=="CEUS":
                misPermisos.CEUS = True
                

    return (misPermisos)

class dia_sprintCreateForm(forms.ModelForm):
    class Meta:
        model = Dia_Sprint
        fields = ("tiempo_estimado",)

class dia_sprintCreateForm2(forms.ModelForm):
    class Meta:
        model = Dia_Sprint
        fields = ("tiempo_real",)
        
def getSprintNro(sprint):
    """
    Funcion utilizada para ordenar una lista en base al numero de sprint
    @param sprint: Objeto Sprint
    @return: en numero de sprint del Sprint
    """
    return sprint.nro_sprint


def sprints(request, proyecto_id, sprint_id, hu_id):
    """
    retorna los sprints de cada proyecto
    
    @param request: Http
    @param proyecto_id: id de un proyecto
    @param sprint_id: id de un sprint
    @param hu_id: id de un user story
    @return: render a project_sprints.html 
    """

    proyecto = Proyectos.objects.get(id = proyecto_id)
    mensaje = ""
    sprint = []
    fmayor = []
    fmenor = []
    tiempo_sprint_dias = 3*5
    tiempo_sprint_horas = 3*5*24
    hus = []
    tiempo_hu_estimado = 0
    tiempo_hu_registrado = 0
    detalles = []
    userStory = []
    usuario = [] #usuario asignado del HU seleccionado
    flujo = [] #flujo al cual esta asignado el HU seleccionado
    prioridad = [] #prioridad del HU seleccionado
    planificar = False #bandera que te permite acceder a la interfaz de modificacion del sprint
    cambiar_fecha = False #bandera que te permite acceder a la interfaz de cambiar fecha fin de un sprint
    fecha_est_fin = [] #fecha estimada del fin de un sprint
    finalizar_sprint = False #bandera que permite acceder a la interfaz para finalizar el sprint
    f_actividad = [] #nro de la actividad de flujo en el que se encuentra el hu (ex: Desarrollo de Flujo 1)
    f_a_estado = [] #nro del estado de la actividad de flujo en que se encuentra el hu (ex: Doing de Desarrollo de Flujo 1)
    fecha_fin_sprint = [] 
    cancelar_hu = False #bandera que te permite acceder a la interfaz de cancelacion de User Story
    users = [] #Equipo del proyecto
    flujos = [] #flujos del proyecto
    prioridades = []
    try:
        sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
        sprints = sorted(sprints, key = getSprintNro, reverse = False)
    except:
        sprints = []

    primer_sprint = True
    for s in sprints:
        if(s.nro_sprint == 1):
            primer_sprint = False

    if request.method == 'POST':
        if request.POST['cambio'] == "Iniciar Proyecto":
            if(primer_sprint):
                mensaje = "Antes de iniciar el proyecto debe tener por lo menos un Sprint"
            else:
                hus_proyecto = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = 1)
                if hus_proyecto:
                    us = True
                    flu = True
                    for hu_proyecto in hus_proyecto:
                        if hu_proyecto.flujo <= 0:
                            mensaje = "No se olvide de asignarle un flujo al User Story: " + str(hu_proyecto.nombre)
                            flu = False
                            break
                        if hu_proyecto.usuario_Asignado <= 0:
                            mensaje = "No se olvide de asignarle un usuario responsable al User Story: " + str(hu_proyecto.nombre)
                            us = False
                            break
                    if us and flu:
                        proyecto.fecha_ini_real = datetime.today().strftime("%Y-%m-%d")
                        mensaje = iniciarSprint(proyecto_id, 1)
                        proyecto = Proyectos.objects.get(id = proyecto_id)
                        sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
                        sprints = sorted(sprints, key = getSprintNro, reverse = False)
                else:
                    mensaje = "Asigne algun User Story al sprint 1 antes de iniciar el proyecto"

        elif request.POST['cambio'] == "Nuevo Sprint":
            crearSprint(proyecto_id)
            sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
            sprints = sorted(sprints, key = getSprintNro, reverse = False)
            
        elif request.POST['cambio'] == "+" or request.POST['cambio'] == "- " or request.POST['cambio'] == "+ " or request.POST['cambio'] == "Iniciar Sprint":
            sprint = Sprint.objects.get(id = sprint_id)
            fecha_fin_sprint = sprint.fecha_fin
            dias_sprint_actual = Dia_Sprint.objects.filter(sprint_id = sprint.id)
            fmayor = dias_sprint_actual.first()
            for dia_sprint_actual in dias_sprint_actual:
                if int(fmayor.fecha.year) < int(dia_sprint_actual.fecha.year):
                    fmayor = dia_sprint_actual
                elif (int(fmayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmayor.fecha.month) < int(dia_sprint_actual.fecha.month)):
                    fmayor = dia_sprint_actual
                elif (int(fmayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmayor.fecha.month) == int(dia_sprint_actual.fecha.month)) and (int(fmayor.fecha.day) < int(dia_sprint_actual.fecha.day)):
                    fmayor = dia_sprint_actual
            fmenor = dias_sprint_actual.first()
            for dia_sprint_actual in dias_sprint_actual:
                if int(fmenor.fecha.year) > int(dia_sprint_actual.fecha.year):
                    fmenor = dia_sprint_actual
                elif (int(fmenor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmenor.fecha.month) > int(dia_sprint_actual.fecha.month)):
                    fmenor = dia_sprint_actual
                elif (int(fmenor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmenor.fecha.month) == int(dia_sprint_actual.fecha.month)) and (int(fmenor.fecha.day) > int(dia_sprint_actual.fecha.day)):
                    fmenor = dia_sprint_actual
            hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            for hu in hus:
                tiempo_hu_estimado = tiempo_hu_estimado + hu.tiempo_Estimado
            hus_registros = UserStoryRegistro.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            for hu_registro in hus_registros:
                tiempo_hu_registrado = tiempo_hu_registrado + hu_registro.tiempo_Real

            if request.POST['cambio'] == "+ ":
                userStory = UserStory.objects.get(id = hu_id)
                detalles = HuCreateForm(initial = {"descripcion":userStory.descripcion, "codigo":userStory.codigo, "tiempo_Estimado":userStory.tiempo_Estimado, "valor_Negocio":userStory.valor_Negocio, "valor_Tecnico":userStory.valor_Tecnico})
                try:
                    usuario = User.objects.get(id = userStory.usuario_Asignado)
                except:
                    usuario = []
                try:
                    flujo = Flujos.objects.get(id = userStory.flujo)
                except:
                    flujo = []
                prioridad = Prioridad.objects.get(id = userStory.prioridad_id)

            if request.POST['cambio'] == "Iniciar Sprint":
                hus_proyecto = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
                if hus_proyecto:
                    us = True
                    flu = True
                    for hu_proyecto in hus_proyecto:
                        if hu_proyecto.flujo < 0:
                            mensaje = "No se olvide de asignarle un flujo al User Story: " + str(hu_proyecto.nombre)
                            flu = False
                            break
                        if hu_proyecto.usuario_Asignado < 0:
                            mensaje = "No se olvide de asignarle un usuario responsable al User Story: " + str(hu_proyecto.nombre)
                            us = False
                            break
                    if us and flu:
                        mensaje = iniciarSprint(proyecto_id, sprint.nro_sprint)
                        sprint = []
                        sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
                        sprints = sorted(sprints, key = getSprintNro, reverse = False)
                else:
                    mensaje = "Asigne algun User Story al sprint " + str(sprint.nro_sprint) + " antes de iniciar el proyecto"

        elif request.POST['cambio'] == "Planificar" or request.POST['cambio'] == "x" or request.POST['cambio'] == " + " or request.POST['cambio'] == " - " or request.POST['cambio'] == "Modificar " or request.POST['cambio'] == "Asignar User Stories":
            sprint = Sprint.objects.get(id = sprint_id)
            planificar = True
            if request.POST['cambio'] == "Asignar User Stories":
                user_stories_id = request.POST.getlist(u'hus[]')
                for user_story_id in user_stories_id:
                    try:
                        hu = UserStory.objects.get(pk=user_story_id)
                        huv = UserStoryVersiones()
                        copiarHU(hu, huv, User.objects.get(username = request.user))
                    except:
                        hu = None
                    hu.sprint = sprint.nro_sprint
                    hu.f_actividad = 1
                    hu.f_a_estado = 1
                    hu.estado_scrum_id = 2
                    hu.save()

            if request.POST['cambio'] == "Modificar ":
                hu = UserStory.objects.get(id = hu_id)
                huv = UserStoryVersiones()
                copiarHU(hu, huv, User.objects.get(username = request.user))
                nuevo_tiempo_estimado = request.POST['tiempo_Estimado']
                if hu.tiempo_Estimado != nuevo_tiempo_estimado:
                    hu.tiempo_Estimado = nuevo_tiempo_estimado
                    #llamar a la funcion de notificar
                    notificarModificacionHU(hu_id, proyecto_id)
                    
                nuevo_valor_negocio = request.POST['valor_Negocio']
                if hu.valor_Negocio != nuevo_valor_negocio:
                    hu.valor_Negocio = nuevo_valor_negocio
                    #llamar a la funcion de notificar
                    notificarModificacionHU(hu_id, proyecto_id)
                    
                nuevo_valor_tecnico = request.POST['valor_Tecnico']
                if hu.valor_Tecnico != nuevo_valor_tecnico:
                    hu.valor_Tecnico = nuevo_valor_tecnico
                    #llamar a la funcion de notificar
                    notificarModificacionHU(hu_id, proyecto_id)
                    
                ouser = User.objects.get(username = request.POST['us'])
                if hu.usuario_Asignado != ouser.id:
                    h = historialResponsableHU()
                    h.hu = hu
                    h.responsable = ouser
                    h.save()
                    notificarCambioResponsableHU(hu.usuario_Asignado, ouser.id, hu_id, proyecto_id)
                    
                hu.usuario_Asignado =  ouser.id
                if request.POST['flujo']:
                    flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
                    oflujo = flujolist.get(descripcion = request.POST['flujo'])
                    if hu.flujo != oflujo.id:
                        hu.flujo = oflujo.id
                        #llamar a la funcion de notificar
                        notificarModificacionHU(hu_id, proyecto_id)
                        
                oprioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
                if hu.prioridad != oprioridad:
                    hu.prioridad = oprioridad
                    #llamar a la funcion de notificar
                    notificarModificacionHU(hu_id, proyecto_id)
                    
                hu.save()

            if request.POST['cambio'] == "x":
                hu = UserStory.objects.get(id = hu_id)
                huv = UserStoryVersiones()
                copiarHU(hu, huv, User.objects.get(username = request.user))
                hu_version_anterior = UserStoryVersiones()
                hu_versiones = UserStoryVersiones.objects.filter(idv = hu.id)
                for hu_version in hu_versiones:
                    if hu_version.sprint != sprint.nro_sprint:
                        hu_version_anterior = hu_version
                        break
                for hu_version in hu_versiones:
                    if hu_version.sprint != sprint.nro_sprint:
                        if hu_version.version > hu_version_anterior.version:
                            hu_version_anterior = hu_version
                #hu_version_anterior es la version mas reciente antes de que el sprint actual se apodere de este User Story
                volverHU(hu, hu_version_anterior)

            if request.POST['cambio'] == " + ":
                userStory = UserStory.objects.get(id = hu_id)
                detalles = HuCreateForm(initial = {"descripcion":userStory.descripcion, "codigo":userStory.codigo, "tiempo_Estimado":userStory.tiempo_Estimado, "valor_Negocio":userStory.valor_Negocio, "valor_Tecnico":userStory.valor_Tecnico})
                equipos = Equipo.objects.filter(proyecto_id = proyecto_id)
                for equipo in equipos:
                    user = User.objects.get(id = equipo.usuario_id)
                    se_encuentra = False
                    for u in users:
                        if u.id == user.id:
                            se_encuentra = True
                    if se_encuentra == False:
                        users.append(user)
                flujos = Flujos.objects.filter(proyecto_id = proyecto_id)
                prioridades = Prioridad.objects.all()
                try:
                    usuario = User.objects.get(id = userStory.usuario_Asignado)
                except:
                    usuario = []
                try:
                    flujo = Flujos.objects.get(id = userStory.flujo)
                except:
                    flujo = []
                try:
                    prioridad = Prioridad.objects.get(id = userStory.prioridad_id)
                except:
                    prioridad = []
                f_actividad = userStory.f_actividad
                try:
                    f_a_estado = Estados.objects.get(id = userStory.f_a_estado)
                except:
                    f_a_estado = []
                try:
                    hus_registros = UserStoryRegistro.objects.filter(idr = userStory.id)
                    for hu_registro in hus_registros:
                        tiempo_hu_registrado = tiempo_hu_registrado + hu_registro.tiempo_Real
                except:
                    tiempo_hu_registrado = 0

            hus2 = UserStory.objects.filter(proyecto_id = proyecto_id, estado_scrum_id = 2)
            hus3 = UserStory.objects.filter(proyecto_id = proyecto_id, estado_scrum_id = 3)
            hus4 = UserStory.objects.filter(proyecto_id = proyecto_id, estado_scrum_id = 4)
            listHus = []
            listHus.append(hus2)
            listHus.append(hus3)
            listHus.append(hus4)
            for huN in listHus:
                for hu in huN:
                    hus.append(hu)

        elif request.POST['cambio'] == "Cambiar Fecha":
            sprint = Sprint.objects.get(id = sprint_id)
            cambiar_fecha = True
            fecha_est_fin = sprint.fecha_est_fin.strftime("%Y-%m-%d")

        elif request.POST['cambio'] == "Cambiar fecha":
            sprint = Sprint.objects.get(id = sprint_id)
            if  request.POST.get('fechaFin', False) < sprint.fecha_ini.strftime("%Y-%m-%d"):
                mensaje = "La fecha estimada de finalizacion debe ser mayor a la de inicio"
                sprint = []
            else:
                if request.POST.get('fechaFin', False) > sprint.fecha_est_fin.strftime("%Y-%m-%d"):
                    d1 = datetime.strptime(sprint.fecha_est_fin.strftime("%Y-%m-%d"), "%Y-%m-%d")
                    d2 = datetime.strptime(request.POST.get('fechaFin', False), "%Y-%m-%d")
                    delta = d2 - d1
                    dia = Dia_Sprint.objects.get(sprint_id = sprint_id, fecha = sprint.fecha_est_fin)
                    dia = dia.dia + 1
                    for i in range(1, delta.days + 1):
                        nuevo_dia_sprint = Dia_Sprint()
                        nuevo_dia_sprint.tiempo_estimado = 8
                        nuevo_dia_sprint.tiempo_real = 0
                        nuevo_dia_sprint.dia = dia
                        nuevo_dia_sprint.sprint_id = sprint.id
                        dia = dia + 1
                        nuevo_dia_sprint.fecha = d1 + timedelta(days=i)
                        nuevo_dia_sprint.save()
                        
                elif request.POST.get('fechaFin', False) < sprint.fecha_est_fin.strftime("%Y-%m-%d"):
                    d2 = datetime.strptime(sprint.fecha_est_fin.strftime("%Y-%m-%d"), "%Y-%m-%d")
                    d1 = datetime.strptime(request.POST.get('fechaFin', False), "%Y-%m-%d")
                    delta = d2 - d1
                    for i in range(1, delta.days + 1):
                        dia_sprint = Dia_Sprint.objects.get(sprint_id = sprint_id, fecha = d1 + timedelta(days=i))
                        dia_sprint.delete()
                    
                sprint.fecha_est_fin = request.POST.get('fechaFin', False)
                sprint.save()
                sprint = []

        elif request.POST['cambio'] == "Finalizar" or request.POST['cambio'] == " -" or request.POST['cambio'] == "Finalizar User Story" or request.POST['cambio'] == "Cancelar esta accion" or request.POST['cambio'] == "Cancelar este user story":
            sprint = Sprint.objects.get(id = sprint_id)
            hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            finalizar_sprint = True
            if request.POST['cambio'] == "Finalizar":
                sprint.estado = 2
                sprint.fecha_fin = datetime.today().strftime("%Y-%m-%d")
                sprint.save()
                for hu in hus:
                    if hu.estado_scrum_id != 5 and hu.estado_scrum_id != 6:
                        huv = UserStoryVersiones()
                        copiarHU(hu, huv, User.objects.get(username = request.user))
                        hu.estado_scrum_id = 4
                        hu.save()
                sprint = Sprint.objects.get(id = sprint_id)
                hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)

            if request.POST['cambio'] == "Finalizar User Story":
                hu = UserStory.objects.get(id = hu_id)
                huv = UserStoryVersiones()
                copiarHU(hu, huv, User.objects.get(username = request.user))
                hu.estado_scrum_id = 5
                hu.save()
                hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            if request.POST['cambio'] == "Cancelar este user story":
                hu = UserStory.objects.get(id = hu_id)
                huv = UserStoryVersiones()
                copiarHU(hu, huv, User.objects.get(username = request.user))
                hu.estado_scrum_id = 6
                hu.motivo_cancelacion = request.POST['motivo_cancelacion']
                hu.save()
                hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)

        elif request.POST['cambio'] == " +":
            sprint = Sprint.objects.get(id = sprint_id)
            hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            finalizar_sprint = True
            userStory = UserStory.objects.get(id = hu_id)
            detalles = HuCreateForm(initial = {"descripcion":userStory.descripcion, "codigo":userStory.codigo, "tiempo_Estimado":userStory.tiempo_Estimado, "valor_Negocio":userStory.valor_Negocio, "valor_Tecnico":userStory.valor_Tecnico})
            usuario = User.objects.get(id = userStory.usuario_Asignado)
            flujo = Flujos.objects.get(id = userStory.flujo)
            prioridad = Prioridad.objects.get(id = userStory.prioridad_id)
            f_actividad = userStory.f_actividad
            f_a_estado = Estados.objects.get(id = userStory.f_a_estado)
            hus_registros = UserStoryRegistro.objects.filter(idr = userStory.id)
            for hu_registro in hus_registros:
                tiempo_hu_registrado = tiempo_hu_registrado + hu_registro.tiempo_Real

        elif request.POST['cambio'] == "Cancelar User Story":
            cancelar_hu = True
            sprint = Sprint.objects.get(id = sprint_id)
            userStory = UserStory.objects.get(id = hu_id)

    #El Scrum Master del proyecto "rol_id = 3"
    scrum = []
    try:
        scrum = Equipo.objects.get(proyecto_id = proyecto_id, usuario_id = request.user.id, rol_id = 3)
    except:
        scrum = Equipo()

    if cancelar_hu:
        return render_to_response('apps/project_sprint_cancelar_hu.html', {"proyecto":proyecto, "userStory":userStory, "sprint":sprint}, context_instance = RequestContext(request))
    elif finalizar_sprint:
        return render_to_response('apps/project_sprints_analizarhu.html', {"proyecto":proyecto, "sprint":sprint,"hus":hus, "userStory":userStory, "detalles":detalles, "usuario":usuario, "flujo":flujo, "prioridad":prioridad, "f_actividad":f_actividad, "f_a_estado":f_a_estado, "tiempo_hu_registrado":tiempo_hu_registrado}, context_instance = RequestContext(request))
    elif cambiar_fecha:
        return render_to_response('apps/project_sprint_fecha_fin.html', {"proyecto":proyecto, "sprint":sprint, "fecha_est_fin":fecha_est_fin}, context_instance = RequestContext(request))
    elif planificar:
        return render_to_response('apps/project_sprint_planificar.html', {"proyecto":proyecto, "sprint":sprint, "hus":hus, "userStory":userStory, "detalles":detalles, "usuario":usuario, "flujo":flujo, "prioridad":prioridad, "f_actividad":f_actividad, "f_a_estado":f_a_estado, "tiempo_hu_registrado":tiempo_hu_registrado, "users":users, "flujos":flujos, "prioridades":prioridades}, context_instance = RequestContext(request))
    else:
        return render_to_response('apps/project_sprints.html', {"proyecto":proyecto, "scrum":scrum, "mensaje":mensaje, "sprints":sprints, "sprint":sprint, "fmayor":fmayor, "fmenor":fmenor, "tiempo_sprint_dias":tiempo_sprint_dias, "tiempo_sprint_horas":tiempo_sprint_horas, "hus":hus, "tiempo_hu_estimado":tiempo_hu_estimado, "tiempo_hu_registrado":tiempo_hu_registrado, "detalles":detalles, "userStory":userStory, "usuario":usuario, "flujo":flujo, "prioridad":prioridad, "fecha_fin_sprint":fecha_fin_sprint}, context_instance = RequestContext(request))
    
def crearSprint(proyecto_id):
    """
    Crea un sprint en el proyecto
    @param proyecto_id: id de un proyecto
    @return: no retorna
    """
    
    primer_sprint = True
    sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
    try:
        nro_sprint = sprints.first().nro_sprint
    except:
        nro_sprint = []

    for sprint in sprints:
        if(sprint.nro_sprint == 1):
            primer_sprint = False
        if(nro_sprint < sprint.nro_sprint):
            nro_sprint = sprint.nro_sprint
            
    if(primer_sprint):
        nro_sprint = 1
    else:
        nro_sprint = nro_sprint + 1

    nuevo_sprint = Sprint()
    nuevo_sprint.nro_sprint = nro_sprint
    nuevo_sprint.estado = 0
    nuevo_sprint.proyecto_id = proyecto_id
    nuevo_sprint.save()

def iniciarSprint(proyecto_id, nro_sprint):
    """
    Crea los dias para un Sprint
    @param proyecto_id: id de un proyecto
    @return: retorna un mensaje cuyo contenido indica si se pudo o no iniciar el sprint
    """
    mensaje = []
    
    sprint = Sprint.objects.get(proyecto_id = proyecto_id, nro_sprint = nro_sprint)
    
    iniciar = True
    otrosSprints = Sprint.objects.filter(proyecto_id = proyecto_id)
    for otroSprint in otrosSprints:
        if(otroSprint.nro_sprint < nro_sprint):
            if(otroSprint.estado != 2):
                iniciar = False
                mensaje = "Antes de iniciar el Sprint " + str(nro_sprint) + " debe finalizar los anteriores"
                break
            
    if(iniciar):
        sprint.fecha_ini = datetime.today().strftime("%Y-%m-%d")
        sprint.save()
        
        d1 = datetime.strptime(sprint.fecha_ini, "%Y-%m-%d")
        for i in range(1, 21):
            d2 = d1 + timedelta(days=i)
        sprint.fecha_est_fin = d2.strftime("%Y-%m-%d")
        sprint.estado = 1
        sprint.save()
        
        delta = d2 - d1
        dia = 1
        for i in range(delta.days + 1):
            nuevo_dia_sprint = Dia_Sprint()
            nuevo_dia_sprint.tiempo_estimado = 8
            nuevo_dia_sprint.tiempo_real = 0
            nuevo_dia_sprint.dia = dia
            nuevo_dia_sprint.sprint_id = sprint.id
            dia = dia + 1
            nuevo_dia_sprint.fecha = d1 + timedelta(days=i)
            nuevo_dia_sprint.save()
        
        proyecto = Proyectos.objects.get(id = proyecto_id)
        proyecto.nro_sprint = nro_sprint
        proyecto.estado_id = 1
        if(nro_sprint == 1):
            proyecto.fecha_ini_real = d1.strftime("%Y-%m-%d")
        proyecto.save()
        
        mensaje = "Sprint " + str(nro_sprint) + " iniciado"
    
    return mensaje

def nuevoSprint(request, proyecto_id, sprint_id):
    """
    Crea un nuevo sprint en el proyecto o da por terminado todos los User Stories del sprint que acaba de terminar
    @param request: Http
    @param proyecto_id: id de un proyecto
    @param sprint_id: id de un sprint
    @return: render a project_sprints si el proyecto ha terminado o render a project_sprint_planificar si se crea un nuevo sprint
    """
    nuevo_sprint = False
    proyecto = Proyectos.objects.get(id = proyecto_id)
    sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
    sprint = Sprint.objects.get(id = sprint_id)
    hus = []
    try:
        hus = UserStory.objects.filter(sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
    except:
        hus = []
    if request.POST['cambio'] == "Dar por finalizado todos los User Stories":
        viejo_sprint = Sprint.objects.get(nro_sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
        viejo_sprint.estado = viejo_sprint.estado + 1
        sprint.delete()
    elif request.POST['cambio'] == "Crear nuevo Sprint":
        viejo_sprint = Sprint.objects.get(nro_sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
        try:
            hus = UserStory.objects.filter(proyecto_id = proyecto.id)
        except:
            hus = []
        viejo_sprint.estado = viejo_sprint.estado + 1
        viejo_sprint.save()
        sprint.estado = 1
        sprint.save()
        proyecto.nro_sprint = proyecto.nro_sprint + 1
        proyecto.save()
        dias_sprint_actual = Dia_Sprint.objects.filter(sprint_id = viejo_sprint.id)
        fmayor = dias_sprint_actual.first()
        for dia_sprint_actual in dias_sprint_actual:
            if int(fmayor.fecha.year) < int(dia_sprint_actual.fecha.year):
                fmayor = dia_sprint_actual
            elif (int(fmayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmayor.fecha.month) < int(dia_sprint_actual.fecha.month)):
                fmayor = dia_sprint_actual
            elif (int(fmayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmayor.fecha.month) == int(dia_sprint_actual.fecha.month)) and (int(fmayor.fecha.day) < int(dia_sprint_actual.fecha.day)):
                fmayor = dia_sprint_actual
        d1 = fmayor.fecha
        dia = 1
        for i in range(1, 21):
            nuevo_dia_sprint = Dia_Sprint()
            nuevo_dia_sprint.tiempo_estimado = 0
            nuevo_dia_sprint.tiempo_real = 0
            nuevo_dia_sprint.dia = dia
            nuevo_dia_sprint.sprint_id = sprint_id
            dia = dia + 1
            nuevo_dia_sprint.fecha = d1 + timedelta(days=i)
            nuevo_dia_sprint.save()
        nuevo_sprint = True
    
    scrum = []
    try:
        scrum = Equipo.objects.get(proyecto_id = proyecto_id, usuario_id = request.user.id, rol_id = 3)
    except:
        scrum = Equipo()
        
    if nuevo_sprint:
        return render_to_response('apps/project_sprint_planificar.html', {"proyecto":proyecto, "sprints":sprints, "hus":hus, "sprint":sprint}, context_instance = RequestContext(request))
    else:
        return render_to_response('apps/project_sprints.html', {"proyecto":proyecto, "sprint":sprint, "sprints":sprints, "scrum":scrum}, context_instance = RequestContext(request)) 

def crearSprints(proyecto_id):
    """
    Genera automaticamente los sprints y sus dias
    @param proyecto_id: id de un proyecto
    @return: no retorna
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    
    d1 = proyecto.fecha_ini
    d2 = proyecto.fecha_est_fin

    delta = d2 - d1
    
    sprint = (delta.days +1)/(7*3)
    resto = (delta.days +1)%(7*3)
    if resto>0:
        sprint = sprint + 1
    
    for i in range(1, sprint+1):
        nuevo_sprint = Sprint()
        nuevo_sprint.nro_sprint = i
        if i == 1:
            nuevo_sprint.estado = 1
        else:
            nuevo_sprint.estado = 0
        nuevo_sprint.proyecto_id = proyecto_id
        nuevo_sprint.save()
    
    sprint = 1
    dia = 1
    for i in range(delta.days + 1):
        nuevo_dia_sprint = Dia_Sprint()
        nuevo_dia_sprint.tiempo_estimado = 8
        nuevo_dia_sprint.tiempo_real = 0
        nuevo_dia_sprint.dia = dia
        nuevo_dia_sprint.sprint_id = Sprint.objects.get(nro_sprint = sprint, proyecto_id = proyecto_id).id
        dia = dia + 1
        if(dia > 7*3):
            dia = 1
            sprint = sprint + 1
        nuevo_dia_sprint.fecha = d1 + timedelta(days=i)
        nuevo_dia_sprint.save()

#def horas(request, hu_id):
def horas(hu_reg, hu_id):
    """
    Asigna horas trabajadas por user story a los dias de cada sprint
    @param request: Http
    @param hu_id: id de un user story
    @return: render a agregarHoras.html con una lista de user stories, lista de proyectos del usuario, el usuario, el formulario del tiempo real de los dias por sprint y un mensaje de error
    """
    
    mensaje = ""
    
    hu = UserStory.objects.get(id = hu_id)
    
    try:
        sprint = Sprint.objects.get(nro_sprint = hu.sprint, proyecto_id = hu.proyecto_id)
        dia_sprint = Dia_Sprint.objects.get(fecha = datetime.today().strftime("%Y-%m-%d"), sprint_id = sprint.id)
        dia_sprint.tiempo_real = int(dia_sprint.tiempo_real) + int(hu_reg.tiempo_Real)
        dia_sprint.save()
        if hu.tiempo_Real == 0:
            hu.fecha_inicio = datetime.today().strftime("%Y-%m-%d")
            hu.estado_scrum_id = 1
        hu.tiempo_Real = int(hu.tiempo_Real) + int(hu_reg.tiempo_Real)
        hu.save()
    except:
        mensaje = "Error: No se sumaron las horas, revise los estados del user story o el rango de fechas del sprint en el cual se encuentra"

    return mensaje

def analizarhus(request, proyecto_id, hu_id):
    """
    despliega una interfaz con los user stories del proyectos donde el Scrum Master analiza y decide si pasan al siguiente sprint
    @param request: Http
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    @return: render a project_sprints_pasarhu.html con el id del proyecto, lista de los user stories en el sprint actual y siguiente y el sprint del cual se quiere saber los detalles
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    userStory = []
    detalles = []
    users = []
    usuario = []
    flujos = []
    flujo = []
    prioridades =[]
    prioridad = []
    sprint = Sprint()
    nuevo_sprint = False
    if request.POST:
        if request.POST['cambio'] == "+" or request.POST['cambio'] == " + ":
            equipos = Equipo.objects.filter(proyecto_id = proyecto_id)
            for equipo in equipos:
                user = User.objects.get(id = equipo.usuario_id)
                se_encuentra = False
                for u in users:
                    if u.id == user.id:
                        se_encuentra = True
                if se_encuentra == False:
                    users.append(user)
            flujos = Flujos.objects.filter(proyecto_id = proyecto_id)
            prioridades = Prioridad.objects.all()
            userStory = UserStory.objects.get(id = hu_id)
            usuario = User.objects.get(id = userStory.usuario_Asignado)
            flujo = Flujos.objects.get(id = userStory.flujo)
            prioridad = Prioridad.objects.get(id = userStory.prioridad_id)
            detalles = HuCreateForm(initial = {"descripcion":userStory.descripcion, "codigo":userStory.codigo, "tiempo_Estimado":userStory.tiempo_Estimado, "valor_Negocio":userStory.valor_Negocio, "valor_Tecnico":userStory.valor_Tecnico})
            if request.POST['cambio'] == " + ":
                sprint = Sprint.objects.get(nro_sprint = proyecto.nro_sprint + 1, proyecto_id = proyecto.id)
                nuevo_sprint = True

        elif request.POST['cambio'] == "Pasar al siguiente Sprint" or request.POST['cambio'] == "Pasar al siguiente Sprint ":
            userStory = UserStory.objects.get(id = hu_id)
            userStory.finalizado = False
            userStory.sprint = int(userStory.sprint) + 1
            userStory.save()
            userStory = []
            if request.POST['cambio'] == "Pasar al siguiente Sprint ":
                sprint = Sprint.objects.get(nro_sprint = proyecto.nro_sprint + 1, proyecto_id = proyecto.id)
                nuevo_sprint = True
        #elif request.POST['cambio'] == "Volver al Sprint anterior":
            #userStory = UserStory.objects.get(id = hu_id)
            #userStory.sprint = int(userStory.sprint) - 1
            #userStory.save()
            #userStory = []
        elif request.POST['cambio'] == "Modificar" or request.POST['cambio'] == "Modificar ":
            hu = UserStory.objects.get(id = hu_id)
            ouser = User.objects.get(username = request.POST['us']) 
            hu.usuario_Asignado =  ouser.id
            flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
            oflujo = flujolist.get(descripcion = request.POST['flujo'])
            hu.flujo = oflujo.id
            oprioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
            hu.prioridad = oprioridad
            hu.save()
            if request.POST['cambio'] == "Modificar ":
                sprint = Sprint.objects.get(nro_sprint = proyecto.nro_sprint + 1, proyecto_id = proyecto.id)
                nuevo_sprint = True
        elif request.POST['cambio'] == " - ":
            sprint = Sprint.objects.get(nro_sprint = proyecto.nro_sprint + 1, proyecto_id = proyecto.id)
            nuevo_sprint = True
    try:
        if nuevo_sprint:
            hus_sprint_actual = UserStory.objects.filter(sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
        else:
            hus_sprint_actual = UserStory.objects.filter(sprint = proyecto.nro_sprint - 1, proyecto_id = proyecto.id)
            
        for hu_sprint_actual in hus_sprint_actual:
            hu_sprint_actual.finalizado = True
            hu_sprint_actual.save()
    except:
        hus_sprint_actual = []
    try:
        if nuevo_sprint:
            hus_sprint_siguiente = UserStory.objects.filter(sprint = proyecto.nro_sprint + 1, proyecto_id = proyecto.id)
        else:
            hus_sprint_siguiente = UserStory.objects.filter(sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
            
        for hu_sprint_siguiente in hus_sprint_siguiente:
            hu_sprint_siguiente.finalizado = False
            hu_sprint_siguiente.save()
    except:
        hus_sprint_siguiente = []
    
    return render_to_response('apps/project_sprints_pasarhu.html', {"proyecto":proyecto, "hus_sprint_actual":hus_sprint_actual, "hus_sprint_siguiente":hus_sprint_siguiente, "userStory":userStory, "detalles":detalles, "users":users, "usuario":usuario, "flujos":flujos, "flujo":flujo, "prioridades":prioridades, "prioridad":prioridad, "nuevo_sprint":nuevo_sprint, "sprint":sprint}, context_instance = RequestContext(request))
