from django.conf.urls import patterns, url

from apps import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^usuario/nuevo', views.nuevo_usuario, name='nuevousuario'),
    url(r'^ingresar/$', views.ingresar, name='ingresar'),    
    url(r'^ingresar/recuperarContrasena/$', views.recuperarContrasena, name='recuperar_contrasena'),
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
    url(r'^modadmin/adminrole/crearrole/$', views.listpermisos, name="crearrol"),
    url(r'^asigpermisos/$', views.listpermisos, name="listpermisos"),
    url(r'^(?P<role_id>\d+)/asignarrol/$', views.asignarrol, name="asignarrol"),
    url(r'^modadmin/adminrole/modificarrol/$', views.listrolesmod, name="listrolesmod"),
    url(r'^(?P<role_id>\d+)/modificarrol/$', views.rolemodify, name="rolemodify"),
    #url(r'^modadmin/adminrole/selectrolmod/$', views.selectrolmod, name="selectrolmod"),
    url(r'^(?P<role_id>\d+)/asignarpermisosmod/$', views.asignarpermisosmod, name="asignarpermisosmod"),
    url(r'^modadmin/adminrole/eliminarrol/$', views.listrolesdel, name="eliminarrol"),
    url(r'^(?P<role_id>\d+)/delrole/$', views.roledelete, name="roledelete"),
    url(r'^modadmin/adminproyecto/$', views.adminproject.as_view(), name="adminproyecto"),
    url(r'^modadmin/adminproyecto/createProject/$', views.crearProyecto, name="createProject"),
    url(r'^(?P<proyecto_id>\d+)/agregarPlantilla/$', views.agregarPlantilla, name='agregarPlantilla'),
  #  url(r'^modadmin/adminproyecto/createProject/$', views.agregarPlantilla, name="agregarPlantilla"),
    url(r'^modadmin/adminflujo/$', views.adminflow.as_view(), name="adminflujo"),
    
    url(r'^modadmin/adminflujo/crearflujo/$', views.crearflujo, name="crearflujo"),
    url(r'^(?P<flow_id>\d+)/setactividades/$', views.setactividades, name="setactividades"),
    
    url(r'^modadmin/adminflujo/editarflujo/$', views.listflowmod, name="listflowmod"),
    url(r'^(?P<flow_id>\d+)/modificarflujo', views.editarflujos, name="editarflujos"),
    url(r'^(?P<flow_id>\d+)/listactivitiesmod', views.listactivitiesmod, name="listactivitiesmod"),
    url(r'^(?P<flow_id>\d+)/(?P<actv_id>\d+)/setactividadesmod', views.setactividadesmod, name="setactividadesmod"),
    
    url(r'^(?P<flow_id>\d+)/(?P<actv_id>\d+)/setactividadesdel', views.setactividadesdel, name="setactividadesdel"),
    
    url(r'^modadmin/adminflujo/eliminarflujo/$', views.listflowdel, name="listflowdel"),
    url(r'^(?P<flow_id>\d+)/flowdelete', views.flowdelete, name="flowdelete"),
    
    url(r'^modadmin/adminuser/asignarrol/$', views.listroleuser, name="listroleuser"),
    url(r'^(?P<user_id>\d+)/asignarrolusuario/$', views.asignarrolusuario, name="asignarrolusuario"),
)
