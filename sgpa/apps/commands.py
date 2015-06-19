# -*- encoding: utf-8 -*-

from django.core.mail import send_mail


from djutils.decorators import async

from apps.models import UserStory, Proyectos, historialResponsableHU, Equipo,\
    UserStoryVersiones, Actividades, Estados
from django.contrib.auth.models import User
from django.db.models.aggregates import Max

@async
def enviarMail(asunto,msg,lista):
    """
    Envia email a una lista de usuarios
    @param asunto: Asunto del email
    @param msg: Cuerpo del email
    @param: lista: lista de usuarios 
    """
    for l in lista:
        send_mail(asunto,
                  msg, 
                  'noreply.sgpa@gmail.com', 
                  [l.email],
                   fail_silently=False)


def notificarNota(proyecto_id,hu_id, nota):
    """
    Prepara un email de notificacion de notas en un user story
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    @param nota: Nota que se agrego a un user story 
    """
    hu = UserStory.objects.get(id = hu_id)
    proyecto = Proyectos.objects.get(id = proyecto_id)
    usuario = User.objects.get(id = hu.usuario_Asignado)
    list = []
    list.append(usuario)
    asunto = 'SGPA - Nueva nota en User Story'
    msg = 'Usuario: '+usuario.username+', se ha agregado una nueva nota al user story: '+hu.nombre+' del proyecto: '+proyecto.nombre+'\n\nNota: \n'+nota 
    enviarMail(asunto, msg, list)
    
    

def notificarModificacionHU(hu_id, proyecto_id):
    """
    Prepara un email de notificacion de cuando de modifica un  user story
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    """
    try:
        huv = UserStoryVersiones.objects.filter(idv = hu_id).latest('version')
        
    except :
        pass  
      
    historial = historialResponsableHU.objects.filter(hu = hu_id)
    hu = UserStory.objects.get(id = hu_id)
    proyecto = Proyectos.objects.get(id = proyecto_id)
    for h in historial:
        list = []
        user = User.objects.get(id = h.responsable.id)
        if user.is_active == True:
            print 'usuario'  
            print user.email 
            
            list.append(user)
            asunto = 'SGPA - Modificacion de User Story'
            
            msg = 'Usuario: '+user.username+', se ha modificado el  user story: '+hu.nombre+' del proyecto: '+proyecto.nombre
            msg = msg + '\n\nDetalles: \n'
            #version actual
            msg = msg + '\n\nVersion actual: \n' 
            msg = msg + '\nNombre: '+hu.nombre +'\nDescripcion: '+hu.descripcion+'\nCodigo: '+str(hu.codigo) +'\nValor Negocio: '+str(hu.valor_Negocio)
            msg = msg + '\nValor Tecnico: '+str(hu.valor_Tecnico) +'\nTiempo Estimado: '+str(hu.tiempo_Estimado) +'\nPrioridad: '+str(hu.prioridad_id)    
    
            try:        
                #Version anterior
                msg = msg + '\n\nVersion anterior: \n' 
                msg = msg + '\nNombre: '+huv.nombre +'\nDescripcion: '+huv.descripcion+'\nCodigo: '+str(huv.codigo) +'\nValor Negocio: '+str(huv.valor_Negocio)
                msg = msg + '\nValor Tecnico: '+str(huv.valor_Tecnico) +'\nTiempo Estimado: '+str(huv.tiempo_Estimado) +'\nPrioridad: '+str(huv.prioridad_id)
            except :
                pass    
            print msg
            enviarMail(asunto, msg, list)

def notificarCambioResponsableHU(old_id, new_id,hu_id, proyecto_id):
    """
    Prepara un email de notificacion de cuando de modifica un  user story
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    """
    print'old'
    print old_id
    print'new'
    print new_id
    historial = historialResponsableHU.objects.filter(hu = hu_id)
    hu = UserStory.objects.get(id = hu_id)
    proyecto = Proyectos.objects.get(id = proyecto_id)
    band = True
    try: 
        Unew = User.objects.get(id = new_id)
        list = []
        list.append(Unew)
        asunto = 'SGPA - Asignacion a User Story'
        msg = 'Usuario: '+Unew.username+', se le ha asignado como responsable del user story: '+hu.nombre+' del proyecto: '+proyecto.nombre
        enviarMail(asunto, msg, list)
        
    
    except:
        Uold = User.objects.get(id = old_id)
        list = []
        list.append(Uold)
        asunto = 'SGPA - Asignacion a User Story'
        msg3 = 'Usuario: '+Uold.username+', se le ha asignado como responsable del user story: '+hu.nombre+' del proyecto: '+proyecto.nombre
        enviarMail(asunto, msg3, list)
        band = False
    
    if band == True:
        try:
            Uold = User.objects.get(id = old_id)
            l = []
            l.append(Uold)
            asunto = 'SGPA - Desasignacion de User Story'
            msg2 = 'Usuario: '+Uold.username+', ha sido desasignado como responsable del user story: '+hu.nombre+' del proyecto: '+proyecto.nombre
            enviarMail(asunto, msg2, l)
       
        except:
            pass

def notificarRegistroTrabajo(hu_id, proyecto_id, detalle,tiempo):
    """
    Prepara un email de notificacion cuando se registra un trabajo en un user story
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    equipo = Equipo.objects.get(proyecto_id = proyecto_id, rol_id = 3)
    hu = UserStory.objects.get(id = hu_id)
    scrumMaster = User.objects.get(id = equipo.usuario_id)
    
    list = []
    list.append(scrumMaster)
    asunto = 'SGPA - Registro de trabajo'
    msg = 'Scrum Master :'+scrumMaster.username+', se ha registrado trabajo en el user story: '+hu.nombre+' del proyecto: '+proyecto.nombre +'\n\nDescripcion del trabajo: \n' + detalle +'\n\nHoras registradas: '+ tiempo
    enviarMail(asunto, msg, list)    

def notificar_pedido_finalizacion(proyecto_id, hu_id):
    """
    Prepara un email de notificacion cuando se solicita revision para finalizacion de un user story
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    equipo = Equipo.objects.get(proyecto_id = proyecto_id, rol_id = 3)
    hu = UserStory.objects.get(id = hu_id)
    usuario = User.objects.get(id = hu.usuario_Asignado)
    scrumMaster = User.objects.get(id = equipo.usuario_id)
            
            
    list = []
    list.append(scrumMaster)
    asunto = 'SGPA - Revision de finalizacion de User Story'
    msg = 'Scrum Master :'+scrumMaster.username+', el usuario: '+usuario.username+ 'ha solicitado la revision del user story: '+hu.nombre\
    +' para su posterior finalizacion \n'\
    +' Proyecto: '+proyecto.nombre \
    +'\n Sprint nro.:' + proyecto.nro_sprint
    enviarMail(asunto, msg, list)
    

def notificar_finalizacion_HU(proyecto_id, hu_id):
    """
    Prepara un email de notificacion de finalizacion de un user story
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    equipo = Equipo.objects.get(proyecto_id = proyecto_id, rol_id = 3)
    hu = UserStory.objects.get(id = hu_id)
    usuario = User.objects.get(id = hu.usuario_Asignado)
    scrumMaster = User.objects.get(id = equipo.usuario_id)
            
            
    list = []
    list.append(usuario)
    asunto = 'SGPA - Finalizacion de User Story'
    msg = 'Usuario :'+usuario.username+', el scrum master: '+scrumMaster.username+ 'ha dado por finalizado el user story: '+hu.nombre\
    +' Proyecto: '+proyecto.nombre \
    +'\n Sprint nro.:' + proyecto.nro_sprint
    enviarMail(asunto, msg, list)
    
def es_ScrumMaster(user_id, proyecto_id, hu_id):
    """
    Verifica si el usuario que ha cambiado el estado del user story fue el Scrum Master, si es asi, 
    prepara un email de notificacion para el usuario encargado del User Story, notificandole que
    se ha cambiado de estado al user story 
    @param user_id: id del usuario que ha cambiado el estado del user story 
    @param proyecto_id: id de un proyecto
    @param hu_id: id de un user story
    """
    proyecto = Proyectos.objects.get(id = proyecto_id)
    equipo = Equipo.objects.get(proyecto_id = proyecto_id, rol_id = 3)
    hu = UserStory.objects.get(id = hu_id)
    usuario = User.objects.get(id = user_id)
    usuario_asignado = User.objects.get(id = hu.usuario_Asignado)
    scrumMaster = User.objects.get(id = equipo.usuario_id)
    
    if usuario == scrumMaster: 
        actividad = Actividades.objects.get(id = hu.f_actividad)
        estado = Estados.objects.get(id = hu.f_a_estado)
        list = []
        list.append(usuario_asignado)
        asunto = 'SGPA - Finalizacion rechazada de User Story'
        msg = 'Usuario :'+usuario_asignado.username+', el scrum master: '+scrumMaster.username+ 'no ha dado por finalizado el user story: '+hu.nombre\
        
        +'\nDetalles de la reprogramacion:'
        +'\n    Proyecto: '+proyecto.nombre \
        +'\n    Sprint nro.:' + proyecto.nro_sprint
        +'\n    Actividad: '+actividad.descripcion \
        +'\n    Estado:' + estado.descripcion
        enviarMail(asunto, msg, list)