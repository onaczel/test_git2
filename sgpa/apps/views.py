from django.shortcuts import get_object_or_404, render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from django.template import RequestContext, loader

from apps.models import Roles, Users_Roles
from django.contrib.auth.models import User

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

class SelectUserView(generic.DetailView):
    model = User
    template_name = 'apps/selectusermod.html'
    #def get_queryset(self):
    #   return User.objects.all()

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=False)
    is_superuser = forms.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "is_superuser")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_superuser = self.cleaned_data["is_superuser"]
        if user.is_superuser == 'null':
            user.is_superuser='FALSE'
        if commit:
            user.save()
        return user 

#'''
def nuevo_usuario(request):
    if request.method=='POST':
        formulario = UserCreateForm(request.POST)
        if formulario.is_valid:
            formulario.save()
        return render_to_response('apps/usercreado.html', context_instance=RequestContext(request))
    else:
        formulario = UserCreateForm()
    return render_to_response('apps/nuevousuario.html', {'formulario':formulario}, context_instance=RequestContext(request))
#'''
    
def ingresar(request):
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
                    return HttpResponseRedirect('/apps/privado')
    #'''Si es usuario normal'''
                else:
                    return HttpResponseRedirect('/apps/privadoNoadmin')
            else:
                return render_to_response('apps/noactivo.html', context_instance=RequestContext(request))
        else:
            return render_to_response('apps/modadmin.html', context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('apps/ingresar.html', {'formulario':formulario}, context_instance=RequestContext(request))



@login_required(login_url='apps/ingresar')
def privado(request):
    usuario = request.user
    return render_to_response('apps/privado.html', {'usuario':usuario}, context_instance=RequestContext(request))

@login_required(login_url='apps/ingresar')
def privadoNoadmin(request):
    usuario = request.user
    return render_to_response('apps/privadoNoadmin.html', {'usuario':usuario}, context_instance=RequestContext(request))

@login_required(login_url='apps/ingresar')
def cerrar(request):
    logout(request)
    return HttpResponseRedirect('/apps/ingresar/')

'''
Cada vista debe tener una clase, o funcion
y un render que llame al template
'''
class modadmin(generic.DetailView):
    template_name = 'apps/modadmin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class modproyecto(generic.DetailView):
    template_name = 'apps/modproyecto.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class adminuser(generic.DetailView):
    template_name="apps/adminuser.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


'''
Se debe crear una funcion que tome una request, y guarde en una variable
la lista de objetos en cuestion, luego enviar esa lista en un render to response
al html que trabajara con el.
Por supuesto, la funcion se debe encontrar en urls
'''
def listuser(request):
    users = User.objects.all()
    return render_to_response("apps/selectusermod.html", {"users":users})

def listuserdel(request):
    users = User.objects.all()
    return render_to_response("apps/selectuserdel.html", {"users":users})

    
def moduser(request):
    #u = get_object_or_404(User, pk=request.POST['user'])
    #return HttpResponseRedirect(reverse('apps:usermodificado'), args=(u.id))
    #return render_to_response('apps/usermodificado.html',context_instance=RequestContext(request))
    #return HttpResponseRedirect(reverse('apps:muser', args=(u.id)))
    #return render_to_response("apps/formmoduser.html", RequestContext(request, {}))
    return render(request, 'apps/selectusermod.html')

def muser(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.POST:
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.is_superuser = form.cleaned_data['is_superuser']
            user.save()
            #form.save()
            return render_to_response("apps/usermodificado.html", RequestContext(request))
    else:
        form = UserCreateForm(initial={'username':'Sergio5', 'email':'sergio2@gmai.com'})
        
        
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('apps/formmoduser.html', args)

def eliminaruser(request):
    return render(request, 'apps/selectuserdel.html')

def deluser(request, id):
    u = get_object_or_404(User, pk=id)

    u.is_active = False
    u.save()
    #return HttpResponseRedirect("apps/usereliminado.html")
    return render_to_response("apps/usereliminado.html", RequestContext(request))
    

        
    #return render_to_response('apps/selectuserdel.html', {"u":u}, context_instance=RequestContext(request))

    
    