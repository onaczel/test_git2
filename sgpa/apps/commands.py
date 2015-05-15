# -*- encoding: utf-8 -*-

from django.core.mail import send_mail


from djutils.decorators import async

from apps.models import UserStory, Proyectos, historialResponsableHU
from django.contrib.auth.models import User

@async
def enviarMail(asunto,msg,lista):
    
    for l in lista:
        send_mail(asunto,
                  msg, 
                  'noreply.sgpa@gmail.com', 
                  [l.email],
                   fail_silently=False)


def notificarNota(proyecto_id,hu_id, nota):
    
    hu = UserStory.objects.get(id = hu_id)
    proyecto = Proyectos.objects.get(id = proyecto_id)
    usuario = User.objects.get(id = hu.usuario_Asignado)
    list = []
    list.append(usuario)
    asunto = 'SGPA - Nueva nota en User Story'
    msg = 'Usuario :'+usuario.username+', se ha agregado una nueva nota al user story: '+hu.nombre+' del proyecto: '+proyecto.nombre+'\n\nNota: \n'+nota 
    enviarMail(asunto, msg, list)
    
    

def notificarModificacionHU(hu_id, proyecto_id):
    
    historial = historialResponsableHU.objects.filter(hu = hu_id)
    hu = UserStory.objects.get(id = hu_id)
    proyecto = Proyectos.objects.get(id = proyecto_id)
    for h in historial:
        user = User.objects.get(id = h.responsable)
        if user.is_active == True:
            list = []
            list.append(user)
            asunto = 'SGPA - Modificacion de User Story'
            msg = 'Usuario :'+user.username+', se ha modificado el  user story: '+hu.nombre+' del proyecto: '+proyecto.nombre
            enviarMail(asunto, msg, list)


#def notificarRegistroTrabajo(hu_id):
            
            
          
            
            
    