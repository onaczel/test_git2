from django.contrib.auth.models import User, AnonymousUser
from apps.models import Proyectos, Roles, Equipo, Flujos, Actividades, UserStory, Sprint, Dia_Sprint
from django.core import mail
from random import choice
from django.contrib.auth.hashers import make_password, check_password
from django.test.client import Client
from django.test import TestCase, RequestFactory
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from apps.views import ingresar, recuperarContrasena, crearProyecto, agregarPlantilla, crearSprints



class test_templates(TestCase):
    
    def test_index(self):
        """
        Prueba de acceso a la pagina de ingreso
        """
        resp = self.client.get('/apps/ingresar/')
        resp.user = AnonymousUser()
        self.assertEqual(resp.status_code, 200)
    
    def test_adminPage(self):
        """
        Prueba de acceso a la pagina de usuario con rol admin
        """
        self.factory = RequestFactory()
        req= self.factory.get('/apps/user_private_admin')
        req.user = AnonymousUser()
        resp = ingresar(req)
        self.assertEqual(resp.status_code, 200)
    
    def test_noAdminPage(self):
        """
        Prueba de acceso a la pagina de usario con rol usuario
        """
        self.factory = RequestFactory()
        req= self.factory.get('/apps/user_private_user')
        req.user = AnonymousUser()
        resp = ingresar(req)        
        self.assertEqual(resp.status_code, 200) 
    
    
    def test_UsuarioNoActivo(self):
        """
        Prueba de acceso a la pagina que notifica que el usuario no esta activo
        """
        self.factory = RequestFactory()
        req= self.factory.get('/apps/user_no_active')
        req.user = AnonymousUser()
        resp = ingresar(req)
        self.assertEqual(resp.status_code, 200) 
        
    def test_UsuarioNoExiste(self):
        """
        Prueba de acceso a la pagina que notifica que el usuario no existe
        """
        self.factory = RequestFactory()
        req= self.factory.get('/apps/user_no_exists')
        req.user = AnonymousUser()
        resp = ingresar(req)
        self.assertEqual(resp.status_code, 200)
        
    def test_RecuperarPwd(self):
        """
        Prueba de acceso a la pagina de recuperacion de contrasena
        """
        self.factory = RequestFactory()
        req= self.factory.get('/apps/user_new_pwd')
        req.user = AnonymousUser()
        resp = recuperarContrasena(req)        
        self.assertEqual(resp.status_code, 200)
        
    def test_RecuperarPwd_usuarioNoValido(self):
        """
        Prueba de acceso a la pagina que notifica que el usuario del cual se requiere recuperar la
        contrasena no es valido
        """
        self.factory = RequestFactory()
        req= self.factory.get('/apps/user_pwd_user_not_valid')
        req.user = AnonymousUser()
        resp = recuperarContrasena(req)        
        self.assertEqual(resp.status_code, 200)
        
    def test_crearProyecto(self):
        """
        Prueba de acceso a la pagina de creacion de proyecto
        """
        us = User()
        us.username = "ariel"
        us.password = "ariel"
        us.email = "ariel@lastdeo.com"
        us.is_active = True
        us.save()
    
        self.factory = RequestFactory()
        req= self.factory.get('apps/project_admin_new.html')
        req.user = AnonymousUser()
        resp = crearProyecto(req, us.id)        
        self.assertEqual(resp.status_code, 200)
    
    
    

class test_login(TestCase):
    
    def test_loginUser(self):
        """
        Prueba de login de un usuario
        """
        #Se crea un usuario para la prueba
        us = User()
        us.username = "ariel"
        us.set_password('ariel')
        us.email = "ariel@lastdeo.com"
        us.is_active = True
        us.save()
        
        c = Client()
        
        
        self.assertTrue(c.login(username = 'ariel', password = 'ariel'), "El usuario no se ha podido loguear")
        
    
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
        

class test_recuperarPwd(TestCase):
    
    def test_recuperarPwd_sendMail(self):
        """
        Prueba envio de mail de recuperacion de contrasena
        """
        mail.outbox = []
        #Se crea un usuario para la prueba
        us = User()
        us.username = "selm"
        us.password = "selm"
        us.email = "selm@outlook.com"
        us.is_active = True
        us.save()
        
        
                
        longitud = 6
        valores = "123456789abcdefghijklmnopqrstuvwxyz?*"
 
        p = ""
        p = p.join([choice(valores) for i in range(longitud)])
                
        us.set_password(p)
        us.save()
        
        mail.send_mail('SGPA-Cambio de clave de accseso', 'Nueva clave de acceso para el usuario <'+us.username+'>: '+ p, 'noreply.sgpa@gmail.com', [us.email], fail_silently=False)
        
        #verifica que un mensaje se ha enviado
        #self.assertEqual(len(mail.outbox), 1)
        
        
        #Verifica que el subject del mensaje es correcto
        self.assertEqual(mail.outbox[0].subject, 'SGPA-Cambio de clave de accseso')
        
        #verifica que se ha enviado correctamente la contrasena nueva
        self.assertEqual(mail.outbox[0].body, 'Nueva clave de acceso para el usuario <'+us.username+'>: '+ p)
        
    def test_recuperarPwd_newPwd(self):
        """
        Prueba de reestablecimiento de contrasena
        """
        #Se crea un usuario para la prueba
        us = User()
        us.username = "selm"
        us.password = "selm"
        us.email = "selm@outlook.com"
        us.is_active = True
        us.save()
        
        longitud = 6
        valores = "123456789abcdefghijklmnopqrstuvwxyz?*"
 
        p = ""
        p = p.join([choice(valores) for i in range(longitud)])
                
        us.set_password(p)
        us.save()
      
        
        self.assertTrue(check_password(p,us.password), 'No se ha modificado la correctamente la contrasena')
            
        
        
class test_proyecto(TestCase):
    
    def test_crearproyecto(self):
        """
        Prueba de creacion correcta de un proyecto
        """
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
    
        self.assertTrue(Proyectos.objects.filter(nombre = 'test').exists(), "El proyecto no se ha creado")   
    
    def test_asignarPlantillaflujo(self):
        """
        Prueba de asociacion de platilla de flujo con proyecto
        """
        #Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        
        #se crea un flujo para la prueba 
        flow = Flujos()        
        flow.descripcion='Desarrollo de software'
        flow.estado = True
        flow.plantilla = True
        flow.save()
        #Se crea la actividad de prueba
        act = Actividades()
        act.descripcion = 'Analisis'
        act.estado = True
        act.flujo = flow
        act.plantilla = True
        act.save()
        
        #se asocia el proyecto a la plantilla
        flow.proyecto = proyecto
        flow.save()
        
        self.assertTrue(Flujos.objects.filter(descripcion = 'Desarrollo de software', id = flow.id, proyecto_id = proyecto.id).exists(), "No se pudo asociar el proyecto a la plantilla")   

        
class test_Flujo(TestCase):
    
    
    def test_crearFlujo(self):
        """
        Prueba de la creacion de un flujo que se utilizara en un proyecto
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        #creacion del flujo de prueba 
        flow = Flujos()
        flow.proyecto = proyecto
        flow.descripcion='Desarrollo de software'
        flow.estado = True
        flow.plantilla = False
        flow.save()
        
        self.assertTrue(Flujos.objects.filter(descripcion = 'Desarrollo de software', proyecto_id = proyecto.id, plantilla = False, id= flow.id).exists(), "No se pudo crear flujo")
    
    
    def test_crearFlujo_plantilla(self):
        """
        Prueba de la creacion de un flujo que se utilizara en un proyecto
        """
        flow = Flujos()
        flow.descripcion='Desarrollo de software'
        flow.estado = True
        flow.plantilla = True
        flow.save()
        
        self.assertTrue(Flujos.objects.filter(descripcion = 'Desarrollo de software', plantilla = True, id=flow.id).exists(), "La plantilla de flujo no se ha creado") 


class test_Actividades(TestCase):
    
    
    def test_crearActividad(self):  
        """
        Prueba de creacion de actividad
        """
        #se crea un flujo para la prueba 
        flow = Flujos()        
        flow.descripcion='Desarrollo de software'
        flow.estado = True
        flow.plantilla = False
        flow.save()
        #Se crea la actividad de prueba
        act = Actividades()
        act.descripcion = 'Analisis'
        act.estado = True
        act.flujo = flow
        act.plantilla = False
        act.save()
        
        self.assertTrue(Actividades.objects.filter(descripcion = 'Analisis', plantilla = False, id= act.id).exists(), "La actividad no se ha creado") 
    
    def test_crearActividad_plantilla(self): 
        """
        Prueba de creacion de plantilla de actividad
        """ 
        #se crea un flujo para la prueba 
        flow = Flujos()        
        flow.descripcion='Desarrollo de software'
        flow.estado = True
        flow.plantilla = True
        flow.save()
        #Se crea la actividad de prueba
        act = Actividades()
        act.descripcion = 'Analisis'
        act.estado = True
        act.flujo = flow
        act.plantilla = True
        act.save()
        
        self.assertTrue(Actividades.objects.filter(descripcion = 'Analisis', plantilla = True, id= act.id).exists(), "La plantilla de actividad no se ha creado") 

          
        
        
class test_equipo(TestCase):        
    
    def test_crearEquipo(self):
        """
        Prueba de creacion de un equipo
        """    
        #Se crea un usuario para la prueba
        us = User()
        us.username = "ariel"
        us.password = "ariel"
        us.email = "ariel@lastdeo.com"
        us.is_active = True
        us.save()        
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()        
        #Se crea un rol para la prueba        
        rol = Roles()
        rol.descripcion = "Scrum Master"
        rol.estado = True
        rol.save()        
        #Se crea el Equipo        
        equipo = Equipo()
        equipo.proyecto = proyecto
        equipo.usuario = us
        equipo.rol = rol
        equipo.save()
        
        self.assertTrue(Equipo.objects.filter(proyecto = proyecto, usuario= us, rol = rol).exists(), "El equipo no se ha creado correctamente")   
        
class test_user_story(TestCase):
    
    def test_crearHU(self):
        """
        Prueba de creacion de un User Story
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        
        us = UserStory()
        us.descripcion = 'test user story'
        us.codigo = 'us1_p1'
        us.tiempo_Estimado = 50
        us.proyecto_id = proyecto.id
        us.save()
        
        #Se comprueba que el proyecto se haya creado con exito
        self.assertTrue(Proyectos.objects.filter(pk = proyecto.id).exists(), "El Proyecto no se ha creado correctamente")
        
        #Se comprueba que el User Story se haya creado con exito
        self.assertTrue(UserStory.objects.filter(descripcion = 'test user story', codigo = 'us1_p1', tiempo_Estimado=50, proyecto_id = proyecto.id).exists(), "El User Story no se ha creado correctamente")
        
    def test_modificarHU(self):
        """
        Prueba de modificacion de User Story
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        
        us = UserStory()
        us.descripcion = 'test user story'
        us.codigo = 'us1_p1'
        us.tiempo_Estimado = 50
        us.proyecto_id = proyecto.id
        us.save()
    
        us.descripcion = 'test 2 user story'
        us.codigo = 'us1_p1 2'
        us.tiempo_Estimado = 51
        us.save()
        
        #Se prueba que exista un User Story con los nuevos campos
        self.assertTrue(UserStory.objects.filter(descripcion = 'test 2 user story', codigo = 'us1_p1 2', tiempo_Estimado = 51, proyecto_id = proyecto.id).exists(), "El User Story no se ha modificado correctamente")
        
        #Se comprueba que efectivamente se hayan modificado los campos, y la combinacion de campos ya modificados, no exista
        self.assertFalse(UserStory.objects.filter(descripcion = 'test user story', codigo = 'us1_p1', tiempo_Estimado=50, proyecto_id = proyecto.id).exists(), "El User Story no se ha modificado correctamente")
        
    def test_campos_obligatorios(self):
        """
        Prueba para confirmar que los campos obligatorios se han guardado correctamente
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        
        us = UserStory()
        us.descripcion = 'test user story'
        us.codigo = 'us1_p1'
        us.tiempo_Estimado = 50
        us.proyecto_id = proyecto.id
        us.save()
        
        #Controlar que el campo descripcion se ha guardado correctamente
        self.assertEqual(us.descripcion, 'test user story', "La descripcion no se ha guardado correctamente")
        #Controlar que el campo de codigo se ha guardado correctamente
        self.assertEqual(us.codigo, 'us1_p1', "El codigo no se ha guardado correctamente")
        #Controlar que el campo de tiempo Estimado se ha guardado correctamente
        self.assertEqual(us.tiempo_Estimado, 50, "El tiempo Estimado no se ha guardado correctamente")
        #Controlar que el campo del proyecto se ha guardado correctamente
        self.assertEqual(us.proyecto_id, proyecto.id, "El id del proyecto no se ha guardado correctamente")
        
    def test_eliminarHU(self):
        """
        Prueba de que un User Story haya cambiado su estado a Inactivo
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        
        us = UserStory()
        us.descripcion = 'test user story'
        us.codigo = 'us1_p1'
        us.tiempo_Estimado = 50
        us.proyecto_id = proyecto.id
        us.save()
        
        us.estado = False
        us.save()
        
        #Se comprueba de que efectivamente se haya cambiado el estado del User Story
        self.assertTrue(UserStory.objects.filter(descripcion = 'test user story', codigo = 'us1_p1', tiempo_Estimado=50, proyecto_id = proyecto.id, estado=False).exists(), "El User Story no se ha eliminado correctamente")
        
    def test_asignar_flujo(self):
        """
        Prueba de asignar un Flujo a un User Story
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        #creacion del flujo de prueba 
        flow = Flujos()
        flow.proyecto = proyecto
        flow.descripcion='Desarrollo de software'
        flow.estado = True
        flow.plantilla = False
        flow.save()
        
        us = UserStory()
        us.descripcion = 'test user story'
        us.codigo = 'us1_p1'
        us.tiempo_Estimado = 50
        us.proyecto_id = proyecto.id
        us.flujo = flow.id
        us.save()
        
        self.assertTrue(UserStory.objects.filter(descripcion = 'test user story', codigo = 'us1_p1', tiempo_Estimado=50, proyecto_id = proyecto.id, flujo=flow.id).exists(), "El User Story no se ha creado correctamente")

    def test_asignar_usuario(self):
        """
        Prueba de asignar un usuario a un User Story
        """
        # Se crea un proyecto para la prueba
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-01-02'
        proyecto.descripcion = 'una prueba de proyecto'
        proyecto.observaciones = 'ninguna'
        proyecto.save()
        #Se crea un usuario para la prueba
        user = User()
        user.username = "ariel"
        user.password = "ariel"
        user.email = "ariel@lastdeo.com"
        user.is_active = True
        user.save() 
        #Se crea un rol para la prueba        
        rol = Roles()
        rol.descripcion = "Scrum Master"
        rol.estado = True
        rol.save()        
        #Se crea el Equipo        
        equipo = Equipo()
        equipo.proyecto = proyecto
        equipo.usuario = user
        equipo.rol = rol
        equipo.save()
        
        #Se crea el User Story
        us = UserStory()
        us.descripcion = 'test user story'
        us.codigo = 'us1_p1'
        us.tiempo_Estimado = 50
        us.proyecto_id = proyecto.id
        us.usuario_Asignado = user.id
        us.save()
        
        self.assertTrue(UserStory.objects.filter(descripcion = 'test user story', codigo = 'us1_p1', tiempo_Estimado=50, proyecto_id = proyecto.id, usuario_Asignado=user.id).exists(), "El User Story no se ha creado correctamente")
        
class test_sprint(TestCase):
    
    def test_crear_sprints(self):
        """
        prueba que los sprints de un proyecto nuevo se hayan creado
        """
        proyecto = Proyectos()
        proyecto.nombre = 'test'
        proyecto.fecha_ini= '2015-01-01'
        proyecto.fecha_est_fin = '2015-02-01'
        proyecto.descripcion = 'una prueba de sprint'
        proyecto.observaciones = 'ninguna'
        proyecto.nro_sprint = 1
        proyecto.save()
        
        proy = Proyectos.objects.filter(nombre = 'test', descripcion = "una prueba de sprint")
        p = proy.first()
        crearSprints(p.id)
        
        self.assertTrue(Sprint.objects.filter(nro_sprint = 1, proyecto_id = p.id).exists(), "El sprint 1 no fue creado")
        self.assertTrue(Sprint.objects.filter(nro_sprint = 2, proyecto_id = p.id).exists(), "El sprint 2 no fue creado")