from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

from apps import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    
    url(r'^ingresar/$', views.ingresar, name='ingresar'),
    url(r'^inicio/(?P<user_id>\d+)/(?P<role_id>\d+)/$', views.inicio, name='inicio'),        
    url(r'^ingresar/recuperarContrasena/$', views.recuperarContrasena, name='recuperar_contrasena'),
    url(r'^user_private_admin/$', views.privado, name='user_private_admin'),
    url(r'^user_private_user/$', views.privadoNoadmin, name='privadoNoadmin'),
    url(r'^cerrar/$', views.cerrar, name='cerrar'),
    #url(r'^modadmin/$', views.modadmin.as_view(), name='modadmin'),
    
    url(r'^(?P<user_logged>\d+)/modadmin/$', views.adminmod, name='adminmod'),
    url(r'^(?P<user_logged>\d+)/modadmin/adminuser/$', views.listuser, name="listuser"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminuser/nuevo', views.nuevo_usuario, name='nuevo_usuario'),
    url(r'^(?P<user_logged>\d+)/modadmin/adminuser/(?P<user_id>\d+)/modificaruser/$', views.muser, name="muser"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminuser/(?P<user_id>\d+)/eliminaruser/$', views.deluser, name="deluser"),
    
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/$', views.listrolesmod, name="listrolesmod"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/crearrole/$', views.listpermisos, name="listpermisos"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/(?P<role_id>\d+)/modificarrol/$', views.rolemodify, name="rolemodify"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/(?P<role_id>\d+)/(?P<proyecto_id>\d+)/modificarrol/rolesetp$', views.rolemodifypermisos, name="rolemodifypermisos"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/(?P<role_id>\d+)/(?P<proyecto_id>\d+)/modificarrol/rolesetp/asignarpermisosmod/$', views.asignarpermisosmod, name="asignarpermisosmod"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/(?P<role_id>\d+)/eliminarrole/$', views.roledelete, name="roledelete"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminrole/(?P<role_id>\d+)/asignarrol/$', views.asignarrol, name="asignarrol"),
    
    url(r'^(?P<user_logged>\d+)/modadmin/adminproyecto/$', views.adminproject, name="adminproject"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminproyecto/crearproyecto/$', views.crearProyecto, name="crearProyecto"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminproyecto/verproyectos/$', views.verProyectos, name="verProyectos"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminproyecto/verproyectosporusuario/$', views.verprojusuario, name="verprojusuario"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminproyecto/crearproyecto/(?P<proyecto_pk>\d+)/agregarPlantilla/$', views.agregarPlantilla, name='agregarPlantilla'),
    
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/$', views.listflowmod, name="listflowmod"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/crearflujo/$', views.crearflujo, name="crearflujo"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/crearflujo/(?P<flow_id>\d+)/setactividades/$', views.setactividades, name="setactividades"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/(?P<flow_id>\d+)/modificarflujo/$', views.editarflujos, name="editarflujos"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/(?P<flow_id>\d+)/modificarflujo/setactividades/$', views.listactivitiesmod, name="listactivitiesmod"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/(?P<flow_id>\d+)/setactividadesmod/(?P<actv_id>\d+)/', views.setactividadesmod, name="setactividadesmod"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/(?P<flow_id>\d+)/eliminarflujo/$', views.flowdelete, name="flowdelete"),
    url(r'^(?P<user_logged>\d+)/modadmin/adminflujo/(?P<flow_id>\d+)/setactividadesdel/(?P<actv_id>\d+)/', views.setactividadesdel, name="setactividadesdel"),
    
    
    #url(r'^modproyecto/$', views.modproyecto.as_view(), name='modproyecto'),
    url(r'^modproyecto/$', views.modproyecto.as_view(), name='modproyecto'),
    
    
    #url(r'^modadmin/adminuser/moduser/$', views.listuser, name='listuser'),    
   # url(r'^modadmin/adminuser/moduser/mod/$', views.moduser, name="moduser"),
   
    url(r'^(?P<usuario_id>\d+)/modproyecto/$', views.listproyectosdelusuario, name='listproyectosdelusuario'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto$', views.accionesproyecto, name='accionesproyecto'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminsprint/(?P<sprint>\d+)/$', views.listsprint, name='listsprint'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/$', views.listhu, name='listhu'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/crearhu/$', views.crearHu, name='crearHu'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/$', views.modificarHu, name="modificarHu"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/editar/$', views.editarHu, name="editarHu"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/registro/$', views.registroHu, name="registroHu"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/registro/nuevo/$', views.crearregistroHu, name="crearregistroHu"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/registro/ver/$', views.verregistroHu, name="verregistroHu"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/eliminar/$', views.eliminarHu, name="eliminarHu"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/setflujo/$', views.listhuflujo, name='listhuflujo'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/asignarflujo/$', views.asignarflujoHu, name='asignarflujoHu'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/setestado/$', views.setEstadoHu, name='setEstadoHu'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/versiones/$', views.listhuversiones, name='listhuversiones'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/versiones/(?P<huv_id>\d+)/cambios/$', views.huvcambios, name='huvcambios'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/versiones/(?P<huv_id>\d+)/volverversion/$', views.volverVersionHU, name='volverVersionHU'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/resumen/$', views.resumenHu, name='resumenHu'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/fileManager/$', views.fileAdjunto, name='fileAdjunto'),

    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/fileManager/versiones/$', views.versionesAdjunto, name='versionesAdjunto'),

    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/agregarnota/$', views.agregarNotaHu, name='agregarNotaHu'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<hu_id>\d+)/notas/$', views.notasHu, name='notasHu'),

    url(r'^modproyecto/accionesproyecto/adminhu/(?P<f_id>\d+)/fileManager/descarga/$', views.send_file, name='send_file'),
    url(r'^(?P<proyecto_id>\d+)/(?P<hu_id>\d+)/modproyecto/accionesproyecto/adminhu/(?P<f_id>\d+)/fileManager/eliminar/$', views.delete_file, name='delete_file'),
    
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/asigparticipante$', views.listasigparticipante, name='listasigparticipante'),
    url(r'^(?P<proyecto_id>\d+)/(?P<usuario_id>\d+)/modproyecto/accionesproyecto/listasigparticipanterol$', views.listasigparticipanterol, name='listasigparticipanterol'),
    url(r'^(?P<proyecto_id>\d+)/(?P<usuario_id>\d+)/modproyecto/accionesproyecto/asigparticipanterol$', views.asigparticipanterol, name='asigparticipanterol'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/listelimparticipante$', views.listelimparticipante, name='listelimparticipante'),
    url(r'^(?P<proyecto_id>\d+)/(?P<usuario_id>\d+)/modproyecto/accionesproyecto/elimparticipante$', views.elimparticipante, name='elimparticipante'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/listflujosproyectos$', views.listflujosproyectos, name='listflujosproyectos'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/listflujosproyectos/agregarPlantillaProyecto$', views.agregarPlantillaProyecto, name='agregarPlantillaProyecto'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/listflujosproyectos/agregarPlantillaProyectoMod$', views.listflujosproyectosMod, name='listflujosproyectosMod'),
    url(r'^(?P<proyecto_id>\d+)/(?P<flujo_id>\d+)/modproyecto/accionesproyecto/listflujosproyectos/eliminarplantillaProyecto$', views.flowdeleteproj, name='flowdeleteproj'),
    url(r'^(?P<proyecto_id>\d+)/(?P<flujo_id>\d+)/(?P<actividad_id>\d+)/modproyecto/accionesproyecto/listflujosproyectos/modificarFlujoProyectoMod$', views.flujosproyectosRequestMod, name='flujosproyectosRequestMod'),
    url(r'^(?P<proyecto_id>\d+)/(?P<flujo_id>\d+)/(?P<actividad_id>\d+)/modproyecto/accionesproyecto/listflujosproyectos/modificarFlujoProyectoModAct$', views.flujosproyectosRequestModAct, name='flujosproyectosRequestModAct'),
    url(r'^(?P<proyecto_id>\d+)/(?P<sprint_id>\d+)/(?P<hu_id>\d+)/modproyecto/accionesproyecto/sprints$', views.sprints, name='sprints'),
    url(r'^(?P<proyecto_id>\d+)/(?P<hu_id>\d+)/modproyecto/accionesproyecto/adminhu/editar/assignUser$', views.userToHU, name='userToHU'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/verCliente$', views.verCliente, name='verCliente'),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/accionesproyecto/(?P<user_id>\d+)/verUsuario$', views.verUser, name='verUser'),
    url(r'^(?P<proyecto_id>\d+)/(?P<hu_id>\d+)/sprint/analizarHu$', views.analizarhus, name='analizarhus'),
    url(r'^(?P<proyecto_id>\d+)/(?P<sprint_id>\d+)/sprint/nuevoSprint$', views.nuevoSprint, name='nuevoSprint'),
  

    url(r'^(?P<hu_id>\d+)/AgregarHoras/$', views.horas, name='horas'),
   
    
    #url(r'^modadmin/adminuser/eliminaruser/$', views.listuserdel, name="eliminaruser"),
    
    
    
    #url(r'^modadmin/adminuser/eliminaruser/del/$', views.eliminaruser),
    
    url(r'^(?P<proyecto_id>\d+)/modproyecto/Roles/$', views.listrolesproj, name="listrolesproj"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/Roles/nuevo/$', views.rolecreateproj, name="rolecreateproj"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/Roles/nuevo/(?P<role_id>\d+)/asignarrol/$', views.asignarrolproj, name="asignarrolproj"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/Roles/(?P<role_id>\d+)/modificar/$', views.rolemodifyproj, name="rolemodifyproj"),
    url(r'^(?P<proyecto_id>\d+)/modproyecto/Roles/(?P<role_id>\d+)/eliminar/$', views.roledeleteproj, name="roledeleteproj"),
    #url(r'^asigpermisos/$', views.listpermisos, name="listpermisos"),
    
    
    
    
    
    #url(r'^modadmin/adminrole/selectrolmod/$', views.selectrolmod, name="selectrolmod"),
    
    
    
    
    
    
  #  url(r'^modadmin/adminproyecto/createProject/$', views.agregarPlantilla, name="agregarPlantilla"),
    
    
    
    
    
    
    
    
    
    
    
    
    url(r'^modadmin/adminflujo/eliminarflujo/$', views.listflowdel, name="listflowdel"),
    
    
    url(r'^modadmin/adminuser/asignarrol/$', views.listroleuser, name="listroleuser"),
    url(r'^modadmin/(?P<user_logged>\d+)/nuevo/(?P<user_id>\d+)/asignarrolusuario/$', views.asignarrolusuario, name="asignarrolusuario"),
    
    url(r'^(?P<user_id>\d+)/modproyecto/$', views.listprojects, name="listprojects"),
    url(r'^(?P<project_id>\d+)/project/$', views.project, name="project"),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
