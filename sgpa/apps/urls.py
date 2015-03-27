from django.conf.urls import patterns, url

from apps import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^usuario/nuevo', views.nuevo_usuario, name='nuevousuario'),
    url(r'^ingresar/$', views.ingresar, name='ingresar'),
    url(r'^user_private_admin/$', views.privado, name='user_private_admin'),
    url(r'^user_private_user/$', views.privadoNoadmin, name='privadoNoadmin'),
    url(r'^cerrar/$', views.cerrar, name='cerrar'),
    url(r'^modadmin/$', views.modadmin.as_view(), name='modadmin'),
    url(r'^modproyecto/$', views.modproyecto.as_view(), name='modproyecto'),
    url(r'^modadmin/adminuser/$', views.adminuser.as_view(), name="adminuser"),
    url(r'^modadmin/adminuser/moduser/$', views.listuser, name='listuser'),
   # url(r'^modadmin/adminuser/moduser/mod/$', views.moduser, name="moduser"),
    url(r'^(?P<user_id>\d+)/muser/$', views.muser, name="muser"),
    url(r'^modadmin/adminuser/eliminaruser/$', views.listuserdel, name="eliminaruser"),
    url(r'^(?P<id>\d+)/deluser/$', views.deluser, name="deluser"),
    url(r'^modadmin/adminuser/eliminaruser/del/$', views.eliminaruser),
    url(r'^modadmin/adminrole/$', views.adminrole.as_view(), name="adminrole"),
    url(r'^modadmin/adminrole/crearrole/$', views.crearRol, name="crearrol"),
    url(r'^asigpermisos/$', views.listpermisos, name="listpermisos"),
    url(r'^(?P<role_id>\d+)/asignarrol/$', views.asignarrol, name="asignarrol"),
)
