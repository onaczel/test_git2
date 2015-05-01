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
    Estados, UserStoryRegistro, archivoAdjunto
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
                    send_mail('SGPA-Cambio de clave de accseso', 'Nueva clave de acceso para el usuario <'+usuario+'>: '+ p, 'noreply.sgpa@gmail.com', [user.email], fail_silently=False)
                
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
    roles = Roles.objects.filter(sistema=False)
    return render_to_response("apps/role_admin_project.html", {"roles":roles, 'proyecto_id':proyecto_id})
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
    @return: render a apps/role_set_permisos.html, lista de permisos, el id y la descripcion del rol que se creo recientemente
    """
    if request.method == 'POST':
        form = RoleModifyForm(request.POST)
        if form.is_valid():
            form.save()
        role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role.sistema = False
        role.save()
        role_id = role.id
        permisos = Permisos.objects.filter(sistema = False)
        return render_to_response("apps/role_set_permisos.html", {"permisos":permisos, "role_id":role_id, "role_descripcion":role.descripcion}, context_instance=RequestContext(request))
    else:
        form = RoleModifyForm()
    
    return render_to_response('apps/role_create.html' ,{'form':form, 'proyecto_id':proyecto_id}, context_instance=RequestContext(request))

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
    lista = request.POST.getlist(u'permisos')
    for p in lista:
        try:
            #permiso = Permisos.objects.get(descripcion=p)
            permiso = Permisos.objects.get(pk=p)
        except Permisos.DoesNotExist:
            permiso = None
        permrol = Permisos_Roles()
        permrol.roles_id = r.id
        permrol.permisos_id = permiso.id
        permrol.save()
        
    return render_to_response("apps/role_created.html", {'sistema':sistema, 'user_logged':user_logged}, context_instance = RequestContext(request))


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
        return rolemodifypermisos(request, user_logged, rol.id)
    else:
        form = RoleModifyForm(initial={'descripcion':rol.descripcion})
    
    return render_to_response('apps/role_modify_form.html' ,{'form':form, "rol":rol , 'user_logged':user_logged}, context_instance=RequestContext(request))
    
def rolemodifypermisos(request, user_logged,  role_id):
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
    return render_to_response("apps/role_set_permisos_mod.html", {"permisos":permisos, "role_id":role_id, "role_descripcion":rol.descripcion, 'user_logged':user_logged}, context_instance=RequestContext(request))
           
def asignarpermisosmod(request, user_logged, role_id):
    """
    Asigna permisos a un rol
    @param request: Http request
    @param role_id: Id de un rol registrado en el sistema
    @return: render a apps/role_modified.html 
    """
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
    proyecto = Proyectos.objects.get(id = proyecto_id)
    flujos = Flujos.objects.filter(proyecto_id = proyecto_id, estado=True)
    actividades = Actividades.objects.filter(plantilla = False , estado=True)
    
    eliminarflujo(request, flujo_id)
    eliminado = True
    return render_to_response("apps/project_modificar_listflujo.html", {"proyecto":proyecto , "flujos":flujos, "actividades":actividades, 'eliminado':eliminado})
    
 
def eliminarflujo(request, flow_id):
    f = get_object_or_404(Flujos, pk=flow_id)
    #f.estado = False
    f.delete()
    return f
###############################creacion de proyecto#################################################################################################

#####################################################################################################################################################

def adminproject(request, user_logged):
    permisos = misPermisos(user_logged, 0)
    rol_permiso = Users_Roles.objects.get(user_id = user_logged)
    rol = Roles.objects.get(pk=rol_permiso.role_id)
    return render_to_response('apps/project_admin.html', {'misPermisos':permisos, 'user_logged':user_logged, 'rol_id':rol.id})
    


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
                proyecto.nro_sprint = 1
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
                send_mail('SGPA-Asignacion a Proyecto',
                       'Su usuario: '+user1.username+', ha sido asignado al proyecto: '+proyecto.nombre+', con el rol de Scrum Master',
                       'noreply.sgpa@gmail.com',
                        [user1.email], 
                        fail_silently=False)
                #Se le envia una notificacion al usuario asignado como Cliente
                send_mail('SGPA-Asignacion a Proyecto',
                       'Su usuario: '+user2.username+', ha sido asignado al proyecto: '+proyecto.nombre+', con el rol de Cliente',
                       'noreply.sgpa@gmail.com',
                        [user2.email], 
                        fail_silently=False)
            
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
    
    crearSprints(proyecto_pk)
    
    return render_to_response('apps/plantilla_anadida.html',{'copyFlujo':copyFlujo,'proyecto':proyecto, 'scrum':scrumMaster,'cli':cliente, 'user_logged':user_logged},context_instance=RequestContext(request))

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
    roles = []
    for rol in Roles.objects.all():
        if rol.estado == True:
            roles.append(rol)
            
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
        users.append(User.objects.get(pk = ur.usuario_id))
        roles.append(Roles.objects.get(pk = ur.rol_id))

    flujo = Flujos.objects.filter(proyecto_id = proyecto_id, estado=True)
    
    actividades = Actividades.objects.all()
    hus = UserStory.objects.filter(proyecto_id = proyecto_id, estado=True)

    for hu in hus:
        if hu.f_a_estado != 0 and hu.f_actividad != 0:
            hu.flujo_posicion = ((hu.f_actividad - 1)*3) + hu.f_a_estado
            hu.save()
    
    tamanolista = []
    for act in actividades:
        tamanolista.append(act)
        tamanolista.append(act)
        tamanolista.append(act)
        
    
        
    return render_to_response("apps/project_acciones.html", {"proyecto":proyecto, "usuario":request.user, "misPermisos":mispermisos, 'users':users, 'roles':roles, 'flujo':flujo, 'actividades':actividades, 'hus':hus, 'tamanolista':tamanolista})




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
    send_mail('SGPA-Desvinculacion de proyecto',
              'Su usuario: '+user.username+', ha sido desvinculado del proyecto: '+proyecto.nombre,
              'noreply.sgpa@gmail.com',
              [user.email], 
              fail_silently=False)
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
    
    return render_to_response('apps/project_crear_flujo.html', {"proyecto":proyecto, "flujos":flujos, "actividades":actividades}, context_instance=RequestContext(request))

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
    
    return render_to_response("apps/project_modificar_listflujo.html", {"proyecto":proyecto , "flujos":flujos, "actividades":actividades})

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
    print proyecto.nombre
    return render_to_response('apps/hu_admin.html', { 'hu':hu, 'proyecto':proyecto, 'proyecto_descripcion':proyecto.nombre, 'misPermisos':mispermisos, 'hu_activos':hu_activos, 'hu_planificados':hu_planificados, 'hu_terminados':hu_terminados, 'hu_descartados':hu_descartados, 'hu_noplanificados':hu_no_planificados})

def gethuid(hu):
    return hu.fecha_creacion
    
def resumenHu(request, proyecto_id, hu_id):
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
    users = []

    eq = Equipo.objects.filter(proyecto_id = proyecto_id)
    for e in eq:
        users.append(User.objects.get(pk=e.usuario_id))
    flujos = Flujos.objects.filter(proyecto_id = proyecto_id)
    prioridades = Prioridad.objects.all()
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    if request.method == 'POST':
        form = HuCreateForm(request.POST)
       
        if form.is_valid():
            form.save()
            #hu = UserStory.objects.get(pk=form.cleaned_data['id'])
            #hu = UserStory.objects.get(codigo  = form.cleaned_data['codigo'])
            hu = UserStory.objects.latest('id')
            hu.proyecto_id = proyecto_id
            hu.fecha_creacion = time.strftime("%Y-%m-%d")
            user = User.objects.get(username = request.POST['us']) 
            hu.usuario_Asignado =  user.id
            flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
            oflujo = flujolist.get(descripcion = request.POST['flujo'])
            hu.flujo = oflujo.id
            prioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
            hu.prioridad = prioridad
            hu.notas = request.POST.get('notas', False)
            hu.save()
            
           
            
            #Se le envia una notificacion al usuario encargado del user story
            send_mail('SGPA-Asignacion a User Story',
                       'Su usuario: '+user.username+', ha sido asignado como el responsable del user story: '+ hu.descripcion+ ', del proyecto: '+proyecto.nombre,
                       'noreply.sgpa@gmail.com',
                        [user.email], 
                        fail_silently=False)
            
            return render_to_response('apps/hu_creado.html',{"proyecto_id":proyecto_id},  context_instance = RequestContext(request))
        else:
            return render_to_response('apps/hu_form_no_valido.html', context_instance = RequestContext(request))
    else:        
        form = HuCreateForm()
        
    return render_to_response('apps/hu_create.html', {"form":form, "proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, 'users':users, 'flujos':flujos, 'prioridades':prioridades}, context_instance = RequestContext(request))

def fileAdjunto(request, proyecto_id, hu_id):
    
    mispermisos = misPermisos(request.user.id, proyecto_id)
    hu = UserStory.objects.get(pk=hu_id)
    proyecto = Proyectos.objects.get(pk = proyecto_id)
    lista = archivoAdjunto.objects.filter(hu_id = hu_id)
   
  
   
        
    if request.method == 'POST':
     
        hu = UserStory.objects.get(id = hu_id)
        file = request.FILES['file']
        adjunto = archivoAdjunto.objects.create(archivo=file, hu = hu)
        adjunto.save()
        var = ""
        var = adjunto.archivo.name
        var = var.split('/')
        var = var[-1]
        adjunto.filename = var
        adjunto.save()
        return render_to_response('apps/hu_fileManager.html', {"lista":lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))

    
    
    return render_to_response('apps/hu_fileManager.html', {"lista":lista,'misPermisos':mispermisos,'hu_id':hu_id,'hu':hu,"proyecto_id":proyecto_id, 'proyecto_nombre':proyecto.nombre, }, context_instance = RequestContext(request))

def send_file(request,f_id):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                           
    """
    archivo = archivoAdjunto.objects.get(id = f_id)
    f = ""
    f = archivo.filename
    filename = '/var/www/adjunto/'+f
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response
    
def editarHu(request, proyecto_id, hu_id):
    """
    editar un User Story existente
    
    @param request: Http
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
    users = []

    eq = Equipo.objects.filter(proyecto_id = proyecto_id)
    for e in eq:
        users.append(User.objects.get(pk=e.usuario_id))

    flujos = Flujos.objects.filter(proyecto_id = proyecto_id)
    prioridades = Prioridad.objects.all()
    user_logged = User.objects.get(username = request.user)
    if request.method == 'POST':
        form = HuCreateForm(request.POST)
        if form.is_valid():
            #form.save()
            copiarHU(hu, huv, user_logged)
            oldnameHU = hu.descripcion
            hu.descripcion = form.cleaned_data['descripcion']
            hu.codigo = form.cleaned_data['codigo']
            hu.tiempo_Estimado = form.cleaned_data['tiempo_Estimado']
            hu.valor_Negocio = form.cleaned_data['valor_Negocio']
            hu.valor_Tecnico = form.cleaned_data['valor_Tecnico']
            hu.proyecto_id = proyecto_id
            user = User.objects.get(username = request.POST['us']) 
            oldUser = hu.usuario_Asignado
            hu.usuario_Asignado =  user.id
            flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
            oflujo = flujolist.get(descripcion = request.POST['flujo'])
            hu.flujo = oflujo.id
            prioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
            hu.prioridad = prioridad
            hu.fecha_modificacion = time.strftime("%Y-%m-%d")
            hu.notas = request.POST.get('notas', False)
            hu.save()
            
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
                    send_mail('Modificacion de User Story',
                       'El User Story: '+oldnameHU+' del proyecto: '+proyecto.nombre+', ha experimentado modificaciones ',
                       'noreply.sgpa@gmail.com',
                        [user.email], 
                        fail_silently=False)  
                
            return render_to_response('apps/hu_modificado.html',{"proyecto_id":proyecto_id, 'hu_id':hu_id, 'hu':hu},  context_instance = RequestContext(request))
        else:
            return render_to_response('apps/hu_form_no_valido.html', context_instance = RequestContext(request))
    else:        
        form = HuCreateForm(initial={'descripcion':hu.descripcion, 'codigo':hu.codigo, 'tiempo_Estimado':hu.tiempo_Estimado, 'valor_Tecnico':hu.valor_Tecnico, 'valor_Negocio':hu.valor_Negocio})

    return render_to_response('apps/hu_modify_fields.html', {"form":form, "proyecto_id":proyecto_id, "hu_id":hu_id, "hu_descripcion":hu.descripcion, 'misPermisos':mispermisos, 'users':users, 'flujos':flujos, 'proyecto_nombre':proyecto.nombre, 'prioridades':prioridades, 'hu':hu}, context_instance = RequestContext(request))

def registroHu(request, proyecto_id, hu_id):
    hu = UserStory.objects.get(pk=hu_id)
    hu_reg = UserStoryRegistro.objects.filter(idr = hu.id)
    
    hu_reg = sorted(hu_reg, key=gethudate, reverse=True)
    proyecto = Proyectos.objects.get(pk=proyecto_id)
    
    return render_to_response('apps/hu_registro.html', {'hu_reg':hu_reg, 'hu':hu, 'proyecto':proyecto}, context_instance=RequestContext(request))

    
def gethudate(hu):
    return hu.fechahora

def crearregistroHu(request, proyecto_id, hu_id):
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
    estado = getEstadoHu(hu_reg)
    
    return render_to_response('apps/hu_registro_mostrar.html', {'hu_reg':hu_reg, 'proyecto':proyecto, 'actividad':actividad.descripcion, 'estado':estado.descripcion, 'flujo':flujo.descripcion})

def getActividadHu(hu):
    """
    Funcion que retorna la Actividad del User Story
    """
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
    """
    count = 0
    estadoslist = Estados.objects.all()
    for est in estadoslist:
        count = count + 1
        if count == hu.f_a_estado:
            estado = Estados.objects.get(pk = est.id)
         
    return estado

def copiarHU(hu, huv, user):
    """
    Funcion que hace una copia de todos los campos de un User Story a otro
    
    @param hu: objeto User Story a copiar
    @param huv: objeto User Story de destino
    @param user: objeto del Usuario que realiza una modificacion en el HU
    """
    huv.idv = hu.id
    huv.descripcion = hu.descripcion
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
    huv.notas = hu.notas
    huv.usercambio = user
    huv.save()

def listhuversiones(request, proyecto_id, hu_id):
    """
    Funcion que retorna la lista de versiones de un determinado User Story
    
    @param request: Http
    @param proyecto_id: id del Proyecto en el que se encuentra el User Story
    @param hu_id: id del User Story en cuestion
    @return: render a hu_list_versiones.html, con el id del User Story, su lista de versiones, y el id del proyecto al que corresponde
    """
    hu = UserStory.objects.get(pk = hu_id)
    huversiones = UserStoryVersiones.objects.filter(idv = hu_id)
    user_logged = request.user
    return render_to_response('apps/hu_list_versiones.html', {'proyecto_id':proyecto_id, 'hu_id':hu_id,'hu':hu, 'hu_descripcion':hu.descripcion, 'hu_versiones':huversiones, 'user_logged':user_logged})
    
def huvcambios(request, proyecto_id, hu_id, huv_id):
    huv = UserStoryVersiones.objects.get(pk=huv_id)
    hu = UserStory.objects.get(pk=hu_id)
    return render_to_response('apps/hu_list_versiones_cambios.html', {'proyecto_id':proyecto_id, 'hu':hu, 'huv':huv})

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
    Cambia el estado de un User Storie
    
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
    actividades = Actividades.objects.filter(flujo_id = hu.flujo)
    estados = Estados.objects.all()
    mispermisos = misPermisos(request.user.id, proyecto_id)
    modificado = False
    if request.method == 'POST':
        #actlist = Actividades.objects.filter(descripcion = request.POST['act'], flujo_id = hu.flujo)
        
        actividadeslist = Actividades.objects.filter(flujo_id = hu.flujo)
        count = 0
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
        
        return render_to_response('apps/project_verCliente.html', {'users':users, 'proyecto':proyecto.descripcion,'proyecto_id':proyecto_id},context_instance = RequestContext(request))

    
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

    return (misPermisos)

class dia_sprintCreateForm(forms.ModelForm):
    class Meta:
        model = Dia_Sprint
        fields = ("tiempo_estimado",)

class dia_sprintCreateForm2(forms.ModelForm):
    class Meta:
        model = Dia_Sprint
        fields = ("tiempo_real",)

def sprints(request, proyecto_id, sprint_id, hu_id):
    """
    retorna los sprints de cada proyecto
    
    @param request: Http
    @param proyecto_id: id de un proyecto
    @param sprint_id: id de un sprint
    @param hu_id: id de un user story
    @return: render a project_sprints.html 
    """
    mensaje = ""
    mensaje_planificar_iniciado = ""
    mensaje_planificar_finalizado = ""
    duracion_dias = 3
    duracion_horas = 3*7*24
    proyecto = Proyectos.objects.get(id = proyecto_id)
    sprint = Sprint()
    #formularios = []
    #tiempos_reales = []
    hus = []
    userStory = UserStory()
    users = []
    flujos = []
    prioridades = []
    usuario = []
    flujo = []
    prioridad = []
    detalles = []
    planificar = False
    pasar_sprint = False
    fmayor = []
    fmenor = []
    nuevo_sprint = False
    if request.method == 'POST':
        if request.POST['cambio'] == "Mostrar" or request.POST['cambio'] == "-":
            sprint = Sprint.objects.get(id = sprint_id)
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
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            except:
                hus = []
            #Mostraba los dias de los Sprints
            #dias_sprint = Dia_Sprint.objects.filter(sprint_id = sprint_id)
            #for d_sprint in dias_sprint:
                #formulario = dia_sprintCreateForm(initial={'tiempo_estimado':d_sprint.tiempo_estimado})      
                #formularios.append(formulario)
                #tiempos_reales.append(d_sprint)
        #PERMITIA LA MODIFICACION DEL CAMPO DE TIEMPO ESTIMADO DE LOS DIAS DE LOS SPRINTS
        #elif request.POST['cambio'] == "Modificar":
            #sprint = Sprint.objects.get(id = sprint_id)
            #dia = Dia_Sprint.objects.get(sprint_id = sprint_id, dia = dia_sprint)
            #formulario = dia_sprintCreateForm(request.POST)
            #if formulario.is_valid():
                #dia.tiempo_estimado = formulario.cleaned_data['tiempo_estimado']
                #dia.save()
            #dias_sprint = Dia_Sprint.objects.filter(sprint_id = sprint_id)
            #for d_sprint in dias_sprint:
                #formulario = dia_sprintCreateForm(initial={'tiempo_estimado':d_sprint.tiempo_estimado})
                #formularios.append(formulario)
                #tiempos_reales.append(d_sprint)
        elif request.POST['cambio'] == "+":
            sprint = Sprint.objects.get(id = sprint_id)
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
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            except:
                hus = []
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
        elif request.POST['cambio'] == "Modificar":
            sprint = Sprint.objects.get(id = sprint_id)
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
            except:
                hus = []
            hu = UserStory.objects.get(id = hu_id)
            ouser = User.objects.get(username = request.POST['us']) 
            hu.usuario_Asignado =  ouser.id
            flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
            oflujo = flujolist.get(descripcion = request.POST['flujo'])
            hu.flujo = oflujo.id
            oprioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
            hu.prioridad = oprioridad
            hu.save()
        elif request.POST['cambio'] == "Planificar":
            sprint = Sprint.objects.get(id = sprint_id)
            planificar = True
            if sprint.estado == 1 and sprint.nro_sprint != 1:
                mensaje_planificar_iniciado = "El sprint ya esta en progreso!"
                planificar = False
            elif sprint.estado == 2:
                mensaje_planificar_finalizado = "El sprint ya ha finalizado!"
                planificar = False
                
            if planificar == False:
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
                    elif (int(fmenor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(fmenor.fecha.month) == int(dia_sprint_actual.fecha.month)) and (int(fmenor.fecha.day) < int(dia_sprint_actual.fecha.day)):
                        fmenor = dia_sprint_actual
            """
            #Calcula si una fecha esta entre un menor y un mayor
            menor_que_fmayor = False
            if int(fmayor.fecha.year) > int(datetime.today().strftime("%Y")):
                menor_que_fmayor = True
            elif (int(fmayor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(fmayor.fecha.month) > int(datetime.today().strftime("%m"))):
                menor_que_fmayor = True
            elif (int(fmayor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(fmayor.fecha.month) == int(datetime.today().strftime("%m"))) and (int(fmayor.fecha.day) > int(datetime.today().strftime("%d"))):
                menor_que_fmayor = True
            mayor_que_fmenor = False
            if int(fmenor.fecha.year) < int(datetime.today().strftime("%Y")):
                mayor_que_fmenor = True
            elif (int(fmenor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(fmenor.fecha.month) < int(datetime.today().strftime("%m"))):
                mayor_que_fmenor = True
            elif (int(fmenor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(fmenor.fecha.month) == int(datetime.today().strftime("%m"))) and (int(fmenor.fecha.day) < int(datetime.today().strftime("%d"))):
                mayor_que_fmenor = True
            
            if menor_que_fmayor and mayor_que_fmenor:
                mensaje_planificar_iniciado = "El sprint ya esta en progreso!"
                planificar = False
            elif menor_que_fmayor == False:
                mensaje_planificar_finalizado = "El sprint ya ha finalizado!"
                planificar = False
            """
            if planificar == False:
                try:
                    hus = UserStory.objects.filter(proyecto_id = proyecto_id, sprint = sprint.nro_sprint)
                except:
                    hus = []
            else:
                try:
                    hus = UserStory.objects.filter(proyecto_id = proyecto_id)
                except:
                    hus = []
        elif request.POST['cambio'] == " + ":
            planificar = True
            sprint = Sprint.objects.get(id = sprint_id)
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id)
            except:
                hus = []
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
        elif request.POST['cambio'] == " - ":
            planificar = True
            sprint = Sprint.objects.get(id = sprint_id)
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id)
            except:
                hus = []
        elif request.POST['cambio'] == "Modificar ":
            planificar = True
            sprint = Sprint.objects.get(id = sprint_id)
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id)
            except:
                hus = []
            hu = UserStory.objects.get(id = hu_id)
            ouser = User.objects.get(username = request.POST['us']) 
            hu.usuario_Asignado =  ouser.id
            flujolist = Flujos.objects.filter(descripcion = request.POST['flujo'], proyecto_id = proyecto_id)
            oflujo = flujolist.get(descripcion = request.POST['flujo'])
            hu.flujo = oflujo.id
            oprioridad = Prioridad.objects.get(descripcion = request.POST['pri'])
            hu.prioridad = oprioridad
            hu.save()
        elif request.POST['cambio'] == "Asignar User Stories":
            planificar = True
            sprint = Sprint.objects.get(id = sprint_id)
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id)
            except:
                hus = []
            user_stories_id = request.POST.getlist(u'hus[]')
            for user_story_id in user_stories_id:
                try:
                    hu = UserStory.objects.get(pk=user_story_id)
                except:
                    hu = None
                hu.sprint = sprint.nro_sprint
                hu.f_actividad = 1
                hu.f_a_estado = 1
                hu.save()
        elif request.POST['cambio'] == "x":
            planificar = True
            sprint = Sprint.objects.get(id = sprint_id)
            try:
                hus = UserStory.objects.filter(proyecto_id = proyecto_id)
            except:
                hus = []
            hu = UserStory.objects.get(id = hu_id)
            hu.sprint = 0
            hu.save()
        elif request.POST['cambio'] == "-->":
            try:
                siguiente_sprint = Sprint.objects.get(nro_sprint = (proyecto.nro_sprint + 1), proyecto_id = proyecto_id)
                es_mayor = False
                sprint_actual = Sprint.objects.get(nro_sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
                dias_sprint_actual = Dia_Sprint.objects.filter(sprint_id = sprint_actual.id)
                mayor = dias_sprint_actual.first()
                for dia_sprint_actual in dias_sprint_actual:
                    if int(mayor.fecha.year) < int(dia_sprint_actual.fecha.year):
                        mayor = dia_sprint_actual
                    elif (int(mayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(mayor.fecha.month) < int(dia_sprint_actual.fecha.month)):
                        mayor = dia_sprint_actual
                    elif (int(mayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(mayor.fecha.month) == int(dia_sprint_actual.fecha.month)) and (int(mayor.fecha.day) < int(dia_sprint_actual.fecha.day)):
                        mayor = dia_sprint_actual

                if int(mayor.fecha.year) < int(datetime.today().strftime("%Y")):
                    es_mayor = True
                elif (int(mayor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(mayor.fecha.month) < int(datetime.today().strftime("%m"))):
                    es_mayor = True
                elif (int(mayor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(mayor.fecha.month) == int(datetime.today().strftime("%m"))) and (int(mayor.fecha.day) < int(datetime.today().strftime("%d"))):
                    es_mayor = True
                else:
                    mensaje = "aun quedan dias por trabajar en este sprint!"
                
                if es_mayor:
                    try:
                        hus = UserStory.objects.filter(sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
                        for hu_sprint_actual in hus:
                            hu_sprint_actual.estado = False
                            hu_sprint_actual.save()
                    except:
                        hus = []
                    proyecto.nro_sprint = proyecto.nro_sprint + 1
                    proyecto.save()
                    sprint_actual.estado = sprint_actual.estado + 1
                    sprint_actual.save()
                    sprint_siguiente = Sprint.objects.get(nro_sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
                    sprint_siguiente.estado = sprint_siguiente.estado + 1
                    sprint_siguiente.save()
                    pasar_sprint = True
            except:
                #crear un nuevo sprint
                es_mayor = False
                sprint_actual = Sprint.objects.get(nro_sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
                dias_sprint_actual = Dia_Sprint.objects.filter(sprint_id = sprint_actual.id)
                mayor = dias_sprint_actual.first()
                for dia_sprint_actual in dias_sprint_actual:
                    if int(mayor.fecha.year) < int(dia_sprint_actual.fecha.year):
                        mayor = dia_sprint_actual
                    elif (int(mayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(mayor.fecha.month) < int(dia_sprint_actual.fecha.month)):
                        mayor = dia_sprint_actual
                    elif (int(mayor.fecha.year) == int(dia_sprint_actual.fecha.year)) and (int(mayor.fecha.month) == int(dia_sprint_actual.fecha.month)) and (int(mayor.fecha.day) < int(dia_sprint_actual.fecha.day)):
                        mayor = dia_sprint_actual

                if int(mayor.fecha.year) < int(datetime.today().strftime("%Y")):
                    es_mayor = True
                elif (int(mayor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(mayor.fecha.month) < int(datetime.today().strftime("%m"))):
                    es_mayor = True
                elif (int(mayor.fecha.year) == int(datetime.today().strftime("%Y"))) and (int(mayor.fecha.month) == int(datetime.today().strftime("%m"))) and (int(mayor.fecha.day) < int(datetime.today().strftime("%d"))):
                    es_mayor = True
                else:
                    mensaje = "aun quedan dias por trabajar en este sprint!"
                    
                if es_mayor:
                    hus = UserStory.objects.filter(sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
                    if hus:
                        sprint = Sprint()
                        sprint.estado = 0
                        sprint.nro_sprint = proyecto.nro_sprint + 1
                        sprint.proyecto_id = proyecto.id
                        sprint.save()
                        for hu_sprint_actual in hus:
                            hu_sprint_actual.estado = False
                            hu_sprint_actual.save()
                        nuevo_sprint = True
                        pasar_sprint = True
                    else:
                        hus = []
                        viejo_sprint = Sprint.objects.get(id = sprint_id)
                        viejo_sprint.estado = viejo_sprint.estado + 1
                        viejo_sprint.save()
                        proyecto.nro_sprint = 0
                        proyecto.save()

    sprints = Sprint.objects.filter(proyecto_id = proyecto_id)
    if pasar_sprint:
        return render_to_response('apps/project_sprints_pasarhu.html', {"proyecto":proyecto, "hus_sprint_actual":hus, "nuevo_sprint":nuevo_sprint, "sprint":sprint}, context_instance = RequestContext(request))
    elif planificar:
        return render_to_response('apps/project_sprint_planificar.html', {"proyecto":proyecto, "sprints":sprints, "hus":hus, "sprint":sprint, "userStory":userStory, "usuario":usuario, "users":users, "flujos":flujos, "prioridades":prioridades, "flujo":flujo, 'prioridad':prioridad, "detalles":detalles, "fmayor":fmayor, "fmenor":fmenor}, context_instance = RequestContext(request))
    else:
        #return render_to_response('apps/project_sprints.html', {"proyecto":proyecto, "sprint":sprint, "sprints":sprints, "formularios":formularios, "tiempos_reales":tiempos_reales, "mensaje":mensaje}, context_instance = RequestContext(request))
        return render_to_response('apps/project_sprints.html', {"proyecto":proyecto, "sprint":sprint, "sprints":sprints, "mensaje":mensaje, "duracion_dias":duracion_dias, "duracion_horas":duracion_horas, "hus":hus, "userStory":userStory, "usuario":usuario, "users":users, "flujos":flujos, "prioridades":prioridades, "flujo":flujo, 'prioridad':prioridad, "detalles":detalles, "fmayor":fmayor, "fmenor":fmenor, "mensaje_planificar_iniciado":mensaje_planificar_iniciado, "mensaje_planificar_finalizado":mensaje_planificar_finalizado}, context_instance = RequestContext(request))

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
        
    if nuevo_sprint:
        return render_to_response('apps/project_sprint_planificar.html', {"proyecto":proyecto, "sprints":sprints, "hus":hus, "sprint":sprint}, context_instance = RequestContext(request))
    else:
        return render_to_response('apps/project_sprints.html', {"proyecto":proyecto, "sprint":sprint, "sprints":sprints}, context_instance = RequestContext(request)) 

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
        nuevo_dia_sprint.tiempo_estimado = 0
        nuevo_dia_sprint.tiempo_real = 0
        nuevo_dia_sprint.dia = dia
        nuevo_dia_sprint.sprint_id = Sprint.objects.get(nro_sprint = sprint, proyecto_id = proyecto_id).id
        dia = dia + 1
        if(dia > 7*3):
            dia = 1
            sprint = sprint + 1
        nuevo_dia_sprint.fecha = d1 + timedelta(days=i)
        nuevo_dia_sprint.save()

def horas(request, hu_id):
    """
    Asigna horas trabajadas por user story a los dias de cada sprint
    @param request: Http
    @param hu_id: id de un user story
    @return: render a agregarHoras.html con una lista de user stories, lista de proyectos del usuario, el usuario, el formulario del tiempo real de los dias por sprint y un mensaje de error
    """
    
    mensaje = ""
    
    if request.POST:
        if request.POST[hu_id] == "Sumar Horas":
            formulario = dia_sprintCreateForm2(request.POST)
            if formulario.is_valid():
                hu = UserStory.objects.get(id = hu_id)
                #Str(datetime.today().strftime("%Y-%m-%d"))
                try:
                    dia_sprint = Dia_Sprint.objects.get(fecha = datetime.today().strftime("%Y-%m-%d"), sprint_id = hu.sprint)
                    dia_sprint.tiempo_real = int(dia_sprint.tiempo_real) + int(formulario.cleaned_data['tiempo_real'])
                    dia_sprint.save()
                except:
                    mensaje = "Error: No se sumaron las horas, Probablemente el User Story ya haya terminado"
            
    user_stories = UserStory.objects.filter(usuario_Asignado = request.user.id, estado = True)
    
    equipos = Equipo.objects.filter(usuario_id=request.user.id)
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

    formulario = dia_sprintCreateForm2()
    
    user = request.user
    u_rol = Users_Roles.objects.get(user_id=user.id)
    rol = Roles.objects.get(pk = u_rol.role_id)
    
    return render_to_response('apps/agregarHoras.html', {"user_stories":user_stories, "proyectos":proyectos, 'rol_id':u_rol.role_id, "user":request.user, "formulario":formulario, "mensaje":mensaje}, context_instance = RequestContext(request))

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
            userStory.estado = True
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
            hu_sprint_actual.estado = False
            hu_sprint_actual.save()
    except:
        hus_sprint_actual = []
    try:
        if nuevo_sprint:
            hus_sprint_siguiente = UserStory.objects.filter(sprint = proyecto.nro_sprint + 1, proyecto_id = proyecto.id)
        else:
            hus_sprint_siguiente = UserStory.objects.filter(sprint = proyecto.nro_sprint, proyecto_id = proyecto.id)
            
        for hu_sprint_siguiente in hus_sprint_siguiente:
            hu_sprint_siguiente.estado = True
            hu_sprint_siguiente.save()
    except:
        hus_sprint_siguiente = []
    
    return render_to_response('apps/project_sprints_pasarhu.html', {"proyecto":proyecto, "hus_sprint_actual":hus_sprint_actual, "hus_sprint_siguiente":hus_sprint_siguiente, "userStory":userStory, "detalles":detalles, "users":users, "usuario":usuario, "flujos":flujos, "flujo":flujo, "prioridades":prioridades, "prioridad":prioridad, "nuevo_sprint":nuevo_sprint, "sprint":sprint}, context_instance = RequestContext(request))
