from django.shortcuts import get_object_or_404, render, render_to_response
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from django.template import RequestContext, loader

from apps.models import Roles, Users_Roles, Permisos, Permisos_Roles, Flujos, Actividades, Actividades_Estados, Proyectos, Equipo
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



class IndexView(generic.DetailView):
    template_name='apps/index.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


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
    
def nuevo_usuario(request):
    """
    Verifica que el formulario es valido y almacena el nuevo usuario en la base de datos
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
            return render_to_response('apps/user_assign_role.html',{'roles':roles, 'user_id':user_id}, context_instance=RequestContext(request))
    else:
        formulario = UserCreateForm(initial={'email':'example@mail.com'})

    return render_to_response('apps/user_create.html', {'formulario':formulario}, context_instance=RequestContext(request))

def listroleuser(request, user_id):
    roles = Roles.objects.all()
    return render_to_response('apps/user_assign_role.html',{'roles':roles, 'user_id':user_id}, context_instance=RequestContext(request))

def asignarrolusuario(request, user_id):
    #role = get_object_or_404(Roles, role_id)
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
    
    return render_to_response('apps/user_created.html', RequestContext(request))
  
    
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
                        
                        #return render_to_response('apps/user_private_user.html', {'listproyectos':listproyectos}, RequestContext(request))
                        return HttpResponseRedirect('/apps/user_private_user')
                else:
                    return render_to_response('apps/user_no_active.html', context_instance=RequestContext(request))
            else:
                return render_to_response('apps/user_no_exists.html', context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('apps/ingresar.html', {'formulario':formulario}, context_instance=RequestContext(request))




def recuperarContrasena(request):
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
    


def listprojects(request, user_id):
    listproyectos = []
    equipo = Equipo.objects.filter(usuario_id=user_id)
    proyectos = Proyectos.objects.all()
    for eq in equipo:
        for p in proyectos:
            if eq.proyecto_id == p.id:
                listproyectos.append(Proyectos(p.id, p.nombre))
    return render_to_response('apps/project_mod.html', {'listproyectos':listproyectos})


def project(request, project_id):
    return render_to_response('apps/project_front_page.html')
                     


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
    
class adminuser(generic.DetailView):
    template_name="apps/user_admin.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class adminrole(generic.DetailView):
    template_name ='apps/role_admin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class adminproject(generic.DetailView):
    template_name = 'apps/project_admin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class adminflow(generic.DetailView):
    template_name = 'apps/flow_admin.html'
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

def listrolesmod(request):
    roles = Roles.objects.all()
    return render_to_response("apps/role_modify.html", {"roles":roles})

def listrolesdel(request):
    roles = Roles.objects.all()
    return render_to_response("apps/role_delete.html", {"roles":roles})

def listflowmod(request):
    flujos = Flujos.objects.filter(estado = True)
    return render_to_response("apps/flow_modify.html", {"flujos":flujos})

def listflowdel(request):
    flujos = Flujos.objects.filter(estado = True)
    return render_to_response("apps/flow_delete.html", {"flujos":flujos})


#Noreversematch es un error de configuracion de url
def listpermisos(request):
    
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
        role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role_id = role.id
        permisos = Permisos.objects.all()
        return render_to_response("apps/role_set_permisos.html", {"permisos":permisos, "role_id":role_id}, context_instance=RequestContext(request))
    else:
        form = RoleCreateForm()
    
    return render_to_response('apps/role_create.html' ,{'form':form}, context_instance=RequestContext(request))

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
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            #form.save()
            return render_to_response("apps/user_modified.html", RequestContext(request))
    else:
        form = UserModifyForm(initial={ 'email':user.email, 'first_name':user.first_name, 'last_name':user.last_name})
        
        
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

     
#MAnager isn't accesible via model isntances, no se pude acceder desde un modelo a 
#una instancia de una clase
def asignarrol(request, role_id):
    r = get_object_or_404(Roles, pk=role_id)
    
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

def rolemodify(request, role_id):
    rol = get_object_or_404(Roles, pk=role_id)
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
        #role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role_id = rol.id
        permisos = Permisos.objects.all()
        proles = Permisos_Roles.objects.all()
        inicializarPermisos()
        for p in permisos:
            for ur in proles:
                if ur.roles_id == role_id and ur.permisos_id == p.id:
                    p.estado = True
                    p.save()
        return render_to_response("apps/role_set_permisos_mod.html", {"permisos":permisos, "role_id":role_id}, context_instance=RequestContext(request))
    else:
        form = RoleCreateForm(initial={'descripcion':rol.descripcion, 'estado':rol.estado})
    
    return render_to_response('apps/role_modify_form.html' ,{'form':form, "rol":rol }, context_instance=RequestContext(request))
    
def asignarpermisosmod(request, role_id):
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

    return render_to_response("apps/role_modified.html", context_instance=RequestContext(request))
    
def inicializarPermisos():
    for p in Permisos.objects.all():
        p.estado = False
        p.save()
        
def roledelete(request, role_id):
    r = get_object_or_404(Roles, pk=role_id)
    
    r.estado = False
    r.save()
    
    return render_to_response("apps/role_deleted.html", RequestContext(request))

class FlowCreateForm(forms.ModelForm):
    class Meta:
        model = Flujos
        fields = ("descripcion", "estado") 
        
class ActivityCreateForm(forms.ModelForm):
    class Meta:
        model = Actividades
        fields = ("descripcion",)
        
        
def crearflujo(request):
    if request.method == 'POST':
        form = FlowCreateForm(request.POST)
        if form.is_valid():
            form.save()
            flow = Flujos.objects.get(descripcion = form.cleaned_data['descripcion'])
            flow_id = flow.id
            formulario = ActivityCreateForm()
        return render_to_response('apps/flow_set_activities.html', {'formulario':formulario, 'flow_id':flow_id}, context_instance=RequestContext(request))
    else:
        form = FlowCreateForm()
    
    return render_to_response('apps/flow_create.html', {'form':form}, context_instance=RequestContext(request))
    
def setactividades(request, flow_id):
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
                return render_to_response('apps/flow_set_activities.html', {'formulario':formulario, 'flow_id':flow_id}, context_instance=RequestContext(request))
            elif request.POST['submit'] == "Guardar y Salir":
                return render_to_response('apps/flow_created.html', context_instance = RequestContext(request))
        else:
            return render_to_response('apps/flow_not_valid.html', context_instance=RequestContext(request))
    else:
        formulario = ActivityCreateForm()
    
    return render_to_response('apps/flow_set_activities.html', {'formulario':formulario, 'flow_id':flow_id}, context_instance=RequestContext(request)) 


def editarflujos(request, flow_id):
    flujo = get_object_or_404(Flujos, pk=flow_id)
    if request.method == 'POST':
        form = FlowCreateForm(request.POST)
        if form.is_valid():
            flujo.descripcion = form.cleaned_data['descripcion']
            flujo.save()
            #form.save()
            
            actividades = Actividades.objects.filter(flujo_id=flow_id)
            
            return render_to_response("apps/flow_set_activities_mod.html", {"actividades":actividades, "flow_id":flow_id}, context_instance=RequestContext(request))
    else:
        form = FlowCreateForm(initial={'descripcion':flujo.descripcion, 'estado':flujo.estado})
    
    return render_to_response('apps/flow_modify_form.html', {'form':form, 'flujo':flujo}, context_instance=RequestContext(request))

def listactivitiesmod(request, flow_id):
    actividades = Actividades.objects.filter(flujo_id=flow_id)
    return render_to_response("apps/flow_set_activities_mod.html", {"actividades":actividades, "flow_id":flow_id}, context_instance=RequestContext(request))

def setactividadesmod(request, flow_id, actv_id):
    f = get_object_or_404(Flujos, pk=flow_id)
    a = get_object_or_404(Actividades, pk=actv_id)
    if request.method == 'POST':
        form = ActivityCreateForm(request.POST)
        if form.is_valid():
            a.descripcion = form.cleaned_data['descripcion']
            a.save()
            return render_to_response("apps/flow_activitie_modified.html", {'flow_id':flow_id}, context_instance=RequestContext(request))
        else:
            return render_to_response('apps/flow_not_valid.html', context_instance=RequestContext(request))
    else:
        form = ActivityCreateForm(initial={'descripcion':a.descripcion})
    
    return render_to_response('apps/flow_set_activities_mod_form.html', {'form':form, 'flow_id':flow_id, 'actv_id':actv_id}, context_instance=RequestContext(request))


def setactividadesdel(request, flow_id, actv_id):
    a = Actividades.objects.get(pk=actv_id)
    a.estado = False
    a.save()
    return render_to_response("apps/flow_activitie_eliminated.html", {"flow_id":flow_id}, context_instance=RequestContext(request))


def flowdelete(request, flow_id):
    f = get_object_or_404(Flujos, pk=flow_id)
    f.estado = False
    f.save()
    return render_to_response("apps/flow_eliminated.html", context_instance=RequestContext(request))
     
'''
def selectrolmod(request):
    try:
        r = Roles.objects.get(pk=request.POST['r'])
    except Roles.DoesNotExist:
        r = None
    
    role_id = r.id
    
    modificarrol(request, role_id)
    
    return render_to_response("apps/index.html", context_instance=RequestContext(request))
    
def modificarrol(request, role_id):
    r = get_object_or_404(Roles, pk=role_id)
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
        #role = Roles.objects.get(descripcion=form.cleaned_data['descripcion'])
        role_id = r.id
        permisos = Permisos.objects.all()
        return render_to_response("apps/role_set_permisos_mod.html", {"permisos":permisos, "role_id":role_id}, context_instance=RequestContext(request))
    else:
        form = RoleCreateForm(intial={'descripcion':r.descripcion, 'estado':r.estado})
    
    return render_to_response('apps/role_modify_form.html' ,{'form':form, "role_id":role_id}, context_instance=RequestContext(request))


    
def asignarpermisosmod(request, role_id):
    r = get_object_or_404(Roles, pk=role_id)
    
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
        
    return render_to_response("apps/role_modified.html", context_instance=RequestContext(request))'''
        
###############################creacion de proyecto###############################



def crearProyecto(request):
        
        if request.method == 'POST':
  
            if  request.POST.get('fechaFin', False) < request.POST.get('fechaInicio', False):
                listUser = User.objects.filter(is_active = True)
                msg = 'La fecha estimada de finalizacion debe ser mayor a la de inicio'
                return render_to_response('apps/project_admin_new.html', {'listuser':listUser, 'user':request.user, 'msg':msg},context_instance=RequestContext(request)) 
            else:
                
                #Creacion de proyecto   
                proyecto = Proyectos()
                proyecto.nombre = request.POST.get('nombre', False)                
                proyecto.descripcion = request.POST.get('descripcion', False)
                proyecto.observaciones = request.POST.get('observaciones', False)
                proyecto.fecha_ini = request.POST.get('fechaInicio', False)
                proyecto.fecha_est_fin = request.POST.get('fechaFin', False)             
                proyecto.save()
                
                #Creacion de equipo
                equipo = Equipo()
                #se obtiene el usuario que se ha escogido
                equipo.usuario = User.objects.get(username = request.POST['sm'])
          
                equipo.proyecto = proyecto
                equipo.rol = Roles.objects.get(descripcion = 'Scrum Master')
                equipo.save()
            
                flujo = Flujos.objects.filter(plantilla = True)
                actividades = Actividades.objects.filter(plantilla = True)
                
               
            
            return render_to_response('apps/project_add_plantilla.html', {'flujo':flujo,'actividades':actividades,'idp':proyecto.id},context_instance=RequestContext(request))
            
            
        else:
            
            listUser = User.objects.filter(is_active = True)
            return render_to_response('apps/project_admin_new.html', {'listuser':listUser, 'user':request.user},context_instance=RequestContext(request)) 

            
        


def agregarPlantilla(request, proyecto_pk):
    
    flujo = Flujos.objects.get(id=request.POST['f'])
    
    copyFlujo = Flujos()
    copyFlujo.descripcion = flujo.descripcion
    copyFlujo.plantilla = False
    copyFlujo.estado = True
    copyFlujo.proyeto_id = proyecto_pk
    copyFlujo.save()                 
    
    actividades = Actividades.objects.filter(flujo_id = request.POST['f'])    
    
    for actividad in actividades:
        copyActividad = Actividades()             
        copyActividad.descripcion = actividad.descripcion
        copyActividad.estado = True
        copyActividad.plantilla = False
        copyActividad.flujo_id = copyFlujo.id
        copyActividad.save()
      
     
    us = Equipo.objects.get(proyecto_id= proyecto_pk, rol_id=3)
    
    scrumMaster = User.objects.get(id = us.usuario_id)
    
    proyecto = Proyectos.objects.get(id = proyecto_pk)
    return render_to_response('apps/plantilla_anadida.html',{'copyFlujo':copyFlujo,'proyecto':proyecto, 'scrum':scrumMaster},context_instance=RequestContext(request))

def listproyectosdelusuario(request, usuario_id):
    """
    Retorna una lista con todos los proyectos del usuario
    """
    #'''Se compara con el registro en la tabla User_Roles'''
    ur = Users_Roles.objects.get(user=usuario_id)
    #'''De la tabla de Roles se trae el id del rol del usuario'''
    rolSistema = Roles.objects.get(descripcion=ur.role)
   
    equipos = Equipo.objects.filter(usuario_id=usuario_id)
    proyectos = []
    rolesProyecto = []
    for equipo in equipos:
        proyectos.append(Proyectos.objects.get(id=equipo.proyecto_id))
    for equipo in equipos:
        rolesProyecto.append(Roles.objects.get(id = equipo.rol_id))
    return render_to_response("apps/project_mod.html", {"proyectos":proyectos, "usuario":request.user, "rol":rolesProyecto ,"rol_id":rolSistema.id})

def listasigparticipante(request, proyecto_id):
    """
    Lista de usuarios que pueden participar en el proyecto
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
        if seEncuentra == True:
            usuarios.append(usuario)

    return render_to_response("apps/project_eliminar_participante.html", {"usuarios":usuarios, "proyecto":proyecto})

def listasigparticipanterol(request, proyecto_id, usuario_id):
    """
    Lista de roles que se pueden asignar a los usuarios
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
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    return render_to_response("apps/project_acciones.html", {"proyecto":proyecto, "usuario":request.user})

def elimparticipante(request, proyecto_id, usuario_id):
    """
    Elimina al usuario del proyecto
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)  
    Equipo.objects.filter(usuario_id = usuario_id, proyecto_id = proyecto_id).delete()
    return render_to_response("apps/project_eliminar_participante_eliminado.html", {"proyecto":proyecto, "usuario":request.user})

def asigparticipanterol(request, proyecto_id, usuario_id):
    """
    Asigna al usuario al proyecto
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
