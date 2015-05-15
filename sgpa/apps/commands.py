# -*- encoding: utf-8 -*-
from django.core.mail.message import EmailMultiAlternatives
from django.http.response import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.defaultfilters import striptags
from django.conf import settings

from djutils.decorators import async
from sgpa.settings import EMAIL_HOST_USER
from apps.models import UserStory, Proyectos
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