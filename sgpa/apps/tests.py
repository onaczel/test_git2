from django.test import TestCase

from django.contrib.auth.models import User




class test_user(TestCase):

    
    
    def test_creacion_usuario(self):
        """
        Prueba la creacion de un usuario
        """
        #Se crea un usuario para la prueba
        us = User()
        us.username = "ariel"
        us.password = "ariel"
        us.email = "ariel@lastdeo.com"
        us.is_active = True
        us.save()
    
        #Se verifica si se ha creado el usuario, consultado si la
        #tabla usuario no esta vacia 
        self.assertTrue(User.objects.all() > 0, "No se ha guardado el usuario")
        
        
    def test_campos_obligatorios(self):
        """
        Se verifica que los campos obligatorios se han guardado
        """
        
        #Se crea un usuario para la prueba
        us = User()
        us.username = "ariel"
        us.password = "ariel"
        us.email = "ariel@lastdeo.com"
        us.is_active = True
        us.save()
    
        
        #Se obtienen los datos del usuario que se ha creado
        user = User.objects.get(username = "ariel")
            
        #Se verifica si se han almacenado los campos obligatorios
        
        #Nombre de usuario 
        self.assertEqual(user.username, "ariel", "No existe el usuario ariel")
        #E-mail
        self.assertEqual(user.email, "ariel@lastdeo.com", "No se ha guardado el email")
        #Contrasena
        self.assertEqual(user.password, "ariel", "No se ha guardado la contrasena")
        
    def test_set_inactivo(self):  
        """
        Se prueba establecer un usuario como inactivo (eliminar)
        """
        #Se crea un usuario para la prueba
        us = User()
        us.username = "ariel"
        us.password = "ariel"
        us.email = "ariel@lastdeo.com"
        us.is_active = True
        us.save()  
        
        #Se simula eliminar el usuario, estableciendo su estado como inactivo
        us.is_active = False;
        
        us.save()
        
        #Se verifica que el estado del usario se ha establecido a inactivo
        self.assertFalse(us.is_active, "El usuario esta activo, no se ha eliminado")