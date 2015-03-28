from django.shortcuts import get_object_or_404, render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from django.template import RequestContext, loader

from apps.models import Roles, Users_Roles, Permisos, Permisos_Roles
from django.contrib.auth.models import User, Group


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.core.context_processors import csrf

import user
from gc import get_objects
from django.contrib.redirects.models import Redirect
from gi.overrides.keysyms import blank
from apt_pkg import Group
from django.forms.fields import RegexField
from cProfile import label
from django.db.models.fields import BooleanField

class IndexView(generic.DetailView):
    template_name='apps/index.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_superuser = forms.BooleanField(required=False)
    first_name = forms.Field(required=True)
    last_name = forms.Field(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2", "is_superuser" )

    def save(self, commit=True):
        """
        Obtiene los datos del formulario creacion de usuario y registra el usuario en el sistema
        """
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_superuser = self.cleaned_data["is_superuser"]
        user.firs_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if user.is_superuser == 'null':
            user.is_superuser='FALSE'
        if commit:
            user.save()
        return user 

class UserModifyForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_superuser = forms.BooleanField(required=False)
    first_name = forms.Field(required=True)
    last_name = forms.Field(required=True)
    
    def __init__(self, *args, **kwargs):
        super(UserModifyForm, self).__init__(*args, **kwargs)
        del self.fields['username']
        
    class Meta:
        model = User
        
        fields = ("first_name", "last_name",  "email", "password1", "password2", "is_superuser" )
        

    def save(self, commit=True):
        """
        Obtiene los datos del formulario de modificacion de usuario y registra los cambios en el sistema
        """
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_superuser = self.cleaned_data["is_superuser"]
        user.firs_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if user.is_superuser == 'null':
            user.is_superuser='FALSE'
        if commit:
            user.save()
        return user 
    
def nuevo_usuario(request):
    """
    Verifica que el formulario es valido y almacena el nuevo usuario en la base de datos
    """
    if request.method=='POST':
        formulario = UserCreateForm(request.POST)
        if formulario.is_valid:
            formulario.save()
            ur = Users_Roles()
            user = User()
            user = User.objects.get(username=formulario.cleaned_data['username'])
            ur.user_id = user.id
            if user.is_superuser:
                ur.role_id = 1
            else:
                ur.role_id = 2
            #CONTROLAR!   
            ur.save()
            return render_to_response('apps/user_created.html', context_instance=RequestContext(request))
    else:
        formulario = UserCreateForm(initial={'email':'example@mail.com'})

    return render_to_response('apps/user_create.html', {'formulario':formulario}, context_instance=RequestContext(request))

    
def ingresar(request):
    """
    Metodo que permite el inicio de sesion en el sistema
    
    Verifica que el usuario este activo y lo redirige a su template correspondiente
    segun su rol en el sistema 
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
                    rol = Roles.objects.get(descripcion=ur.role)
    #'''Si el usuario es administrador'''
                    if rol.id == 1:
                        return HttpResponseRedirect('/apps/user_private_admin')
    #'''Si es usuario normal'''
                    else:
                        return HttpResponseRedirect('/apps/user_private_user')
                else:
                    return render_to_response('apps/user_no_active.html', context_instance=RequestContext(request))
            else:
                return render_to_response('apps/user_no_exists.html', context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('apps/ingresar.html', {'formulario':formulario}, context_instance=RequestContext(request))



@login_required(login_url='apps/ingresar')
def privado(request):
    """
    Retorna el template correspondiente a un usuario con rol Administrador
    """
    usuario = request.user
    return render_to_response('apps/user_private_admin.html', {'usuario':usuario}, context_instance=RequestContext(request))

@login_required(login_url='apps/ingresar')
def privadoNoadmin(request):
    """
    Retorna el template correspondiente a un usuario con rol Usuario
    """
    usuario = request.user
    return render_to_response('apps/user_private_user.html', {'usuario':usuario}, context_instance=RequestContext(request))

@login_required(login_url='apps/ingresar')
def cerrar(request):
    """
    Recibe un request y cierra la sesion correspondiente
    """
    logout(request)
    return HttpResponseRedirect('/apps/ingresar/')

'''
Cada vista debe tener una clase, o funcion
y un render que llame al template
'''
class modadmin(generic.DetailView):
    template_name = 'apps/admin_mod.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class modproyecto(generic.DetailView):
    template_name = 'apps/project_mod.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class adminuser(generic.DetailView):
    template_name="apps/user_admin.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class adminrole(generic.DetailView):
    template_name ='apps/role_admin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


'''
Se debe crear una funcion que tome una request, y guarde en una variable
la lista de objetos en cuestion, luego enviar esa lista en un render to response
al html que trabajara con el.
Por supuesto, la funcion se debe encontrar en urls
'''
def listuser(request):
    """
    Retorna una lista con todos los usuarios del sistema y lo envia al template
    de modificacion de usuario
    """
    users = User.objects.all()
    return render_to_response("apps/user_select_mod.html", {"users":users})

def listuserdel(request):
    """
    Retorna una lista con todos los usuarios del sistema y lo envia al template
    de eliminacion de usuario
    """
    users = User.objects.all()
    return render_to_response("apps/user_select_del.html", {"users":users})
#Noreversematch es un error de configuracion de url
def listpermisos(request):
    
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
        #return render_to_response('apps:listpermisos', context_instance=RequestContext(request))
        #return render(request, 'apps/ingresar.html') 
        role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role_id = role.id
        permisos = Permisos.objects.all()
        return render_to_response("apps/role_set_permisos.html", {"permisos":permisos, "role_id":role_id}, context_instance=RequestContext(request))
    else:
        form = RoleCreateForm()
    
    return render_to_response('apps/role_create.html' ,{'form':form}, context_instance=RequestContext(request))
    #permisos = Permisos.objects.all()
    #return render_to_response("apps/role_set_permisos.html", {"permisos":permisos})
   
#def asigpermisos(request, role_id):
#    get_object_or_404(Roles, role_id)
#    if  request.method == 'POST':

    
#def moduser(request):
    #return render(request, 'apps/user_select_mod.html')

def muser(request, user_id):
    """
    Metodo que obtiene los campos modificados del formulario de modificacion de usuario
    """
    user = get_object_or_404(User, pk=user_id)
    if request.POST:
        form = UserModifyForm(request.POST)
        if form.is_valid():
            #user.save(update_field=['username'])
            user.set_password(form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.is_superuser = form.cleaned_data['is_superuser']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            #form.save()
            return render_to_response("apps/user_modified.html", RequestContext(request))
    else:
        form = UserModifyForm(initial={ 'email':user.email, 'is_superuser':user.is_superuser, 'first_name':user.first_name, 'last_name':user.last_name})
        
        
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('apps/user_form_mod.html', args)

def eliminaruser(request):
    return render(request, 'apps/user_select_del.html')

def deluser(request, id):
    u = get_object_or_404(User, pk=id)

    u.is_active = False
    u.save()
    return render_to_response("apps/user_deleted.html", RequestContext(request))

class RoleCreateForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = ("descripcion", "estado")

     
def crearRol(request):
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
        return render_to_response('apps:listpermisos', context_instance=RequestContext(request))
        #return render(request, 'apps/ingresar.html') 
    else:
        form = RoleCreateForm()
    
    return render_to_response('apps/role_create.html' ,{'form':form}, context_instance=RequestContext(request))
#MAnager isn't accesible via model isntances, no se pude acceder desde un modelo a 
#una instancia de una clase
def asignarrol(request, role_id):
    r = get_object_or_404(Roles, pk=role_id)
    if request.POST:
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
            
        return render_to_response("apps/role_created.html", RequestContext(request))
    #try:
        
    #if request.method == 'POST':
     #   list_permisos = request.POST.getlist('lista')
        #perm = 
    return render_to_response("apps/user_deleted.html", RequestContext(request))