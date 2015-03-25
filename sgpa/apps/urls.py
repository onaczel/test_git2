from django.conf.urls import patterns, url

from apps import views

urlpatterns = patterns('',
    url(r'^usuario/nuevo', views.nuevo_usuario, name='nuevousuario'),
    url(r'^ingresar/$', views.ingresar, name='ingresar'),
    url(r'^privado/$', views.privado, name='privado'),
    url(r'^privadoNoadmin/$', views.privadoNoadmin, name='privadoNoadmin'),
    url(r'^cerrar/$', views.cerrar, name='cerrar'),
    url(r'^modadmin/$', views.modadmin.as_view(), name='modadmin'),
    url(r'^modproyecto/$', views.modproyecto.as_view(), name='modproyecto'),
    url(r'^modadmin/adminuser/$', views.adminuser.as_view(), name="adminuser"),
    url(r'^modadmin/adminuser/moduser/$', views.listuser, name='listuser'),
    url(r'^modadmin/adminuser/moduser/mod/$', views.moduser, name="moduser"),
    #url(r'^modadmin/adminuser/moduser/mod2/$', views.muser, name="moduser2"),
    #url(r'^modadmin/adminuser/moduser/mod/ok/$', views.usermodificado, name="usermod"),
    
    url(r'^(?P<user_id>\d+)/muser/$', views.muser, name="muser"),
    
    url(r'^modadmin/adminuser/eliminaruser/$', views.listuserdel, name="eliminaruser"),
    url(r'^(?P<id>\d+)/deluser/$', views.deluser, name="deluser"),
    url(r'^modadmin/adminuser/eliminaruser/del/$', views.eliminaruser),
    
    #url(r'^modifyUser/$', views.muser, name="hola"),
)
