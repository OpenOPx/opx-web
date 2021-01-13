from django.conf import settings
from django.http.response import JsonResponse
from django.shortcuts import render
from django.db import (connection, transaction)
from myapp import models
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from rest_framework_simplejwt.backends import TokenBackend

#========================== Utilidades =============================

##
# @brief Función que formatea el resultado de una consulta de base de datos
# @param cursor Cursor que contiene el resultado de la consulta
# @return lista de diccionarios
#
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

##
# @brief Recurso que provee el listado de los géneros del sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def listadoGeneros(request):

    generos = models.Gender.objects.all().values()

    data = {
        'code': 200,
        'generos': list(generos),
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Recurso que provee el listado de niveles educativos del sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def listadoNivelesEducativos(request):

    educationLevel = models.EducationLevel.objects.all().values()

    data = {
        'code': 200,
        'nivelesEducativos': list(educationLevel),
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Recurso que provee el listado de barrios de Santiago de Cali
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def listadoBarrios(request):

    neighborhood = models.Neighborhood.objects.all().order_by('neighb_name').values()

    data = {
        'code': 200,
        'barrios': list(neighborhood),
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Función que provee la instancia del modelo usuario en base al Token de sesión
# @param request Instancia HttpRequest
# @return instancia del modelo Usuario
#
def usuarioAutenticado(request):

    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
    # consultando el usuario
    user = models.User.objects.get(pk=tokenDecoded['user_id'])

    return user

##
# @brief Función que provee un parametro del sistema
# @param parametro Identificación del parametro
# @return cadena con el valor de parámetro del sistema
#
def obtenerParametroSistema(parametro):

    parametro = models.Parametro.objects.get(pk=parametro)

    if parametro is not None:
        response = parametro.paramvalor
    else:
        response = None

    return response

def getPersonsByTeam(team_id):

    return []

def getPersonsIdByProject(proj_id):
    persons = []
    query = "SELECT DISTINCT tp.person_id \
	        FROM opx.team_person as tp \
	        INNER JOIN opx.project_team AS pt ON tp.team_id = pt.team_id \
	        WHERE pt.project_id = '"+str(proj_id)+"';"
    with connection.cursor() as cursor:
        cursor.execute(query)
        person_ids = dictfetchall(cursor)
        for pers_id in list(person_ids):
            persons.append(pers_id['person_id'])
    return persons

##
# @brief Función que provee el listado de correos electrónicos de los integrantes de un proyecto
# @param proyid Identificación de un proyecto
# @return Lista
#
def obtenerEmailsEquipo(proyid):

    with connection.cursor() as cursor:
        query = "SELECT useremail \
                FROM opx.project AS pr \
                INNER JOIN opx.project_team AS pt ON pt.project_id = pr.proj_id \
                INNER JOIN opx.team_person AS tp ON tp.team_id = pt.team_id \
                INNER JOIN opx.person AS person ON person.pers_id = tp.person_id \
                INNER JOIN opx.user AS us ON us.userid = person.user_id"
        cursor.execute(query)
        correos = dictfetchall(cursor)
        return JsonResponse(correos, safe=False)

##
# @brief Recurso que provee el correo electrónico de un usuario
# @param userid Identificación de un usuario
# @return cadena que contiene el correo electrónico del usuario
#
def obtenerEmailUsuario(userid):

    usuario = models.Usuario.objects.get(pk = userid)

    email = [usuario.useremail]

    return email

##
# @brief Función que retorna una plantilla HTML cuando no se encuentra un recurso en el sistema
# @param request Instancia HttpRequest
# @param exception excepción opcional
# @return plantilla HTML
#
def notFoundPage(request, exception=None):
    return render(request, "error/404.html")

##
# @brief Función que retorna una plantilla HTML cuando ocurre un error en el sistema
# @param request Instancia HttpRequest
# @param exception excepcion opcional
# @return plantilla HTML
#
def serverErrorPage(request, exception=None):
    return render(request, "error/500.html")

#
#
#COMENTAR LUEGO XD

def puntajeTarea(tarid):
    tarea = models.Task.objects.get(pk = tarid)
    if tarea.task_type_id == 1:
        encuestas = models.Survery.objects.filter(task__task_id__exact = tarea.task_id)
        progreso = (len(encuestas)/ tarea.task_quantity)
        tarea.task_completness = progreso
        if progreso == 1:
            tarea.isactive = 0
        tarea.save()
    if tarea.task_type_id == 2:
        tareasValidadas += 1  


def puntajeProyecto( proyid):
    proyecto = (models.Project.objects.get(pk = proyid))
    tareas = models.Task.objects.filter(project_id__exact = proyid)
    progresoProyecto = 0
    prioridadTotal = 0
    for tarea in tareas:
        if tarea.task_type_id == 1:
            prioridadTotal += tarea.task_priority.priority_number

    for tarea in tareas:
        if tarea.task_type_id == 1:
            prioridadDeTarea = tarea.task_priority.priority_number
            pesoDeTarea= (prioridadDeTarea/prioridadTotal) * 100
            progresoProyecto += tarea.task_completness * pesoDeTarea
    if progresoProyecto == 100:
        proyecto.isactive = 0
    proyecto.proj_completness = progresoProyecto
    proyecto.save()


def puntajePersona(persid):
    persona = models.Person.objects.get(pk = persid)
    puntajeDePersona = 0

    query = "select su.survery_id, su.person_id, tp.priority_number \
            from opx.person as persona \
            inner join opx.survery as su on su.person_id = persona.pers_id  \
            inner join opx.task as tk on tk.task_id = su.task_id \
            inner join opx.task_priority as tp on tp.priority_id = tk.task_priority_id \
            where persona.pers_id = '"+persid+"';"

    with connection.cursor() as cursor:
        cursor.execute(query)
        encuestas = dictfetchall(cursor)

    for encuesta in list(encuestas):
        puntajeDePersona += encuesta['priority_number']

    persona.pers_score = puntajeDePersona
    persona.save()
    equipos = equiposDePersona(persid)
    for equipo in list(equipos):
        puntajeEquipo(str(equipo['team_id']))


def puntajeEquipo(teamid):
    equipo = models.Team.objects.get(pk = teamid)  
    puntajeDeEquipo = 0
    query = "select pr.pers_score from opx.team as tm \
            inner join opx.team_person as tp on tp.team_id = tm.team_id  \
            inner join opx.person as pr on pr.pers_id = tp.person_id \
            where tm.team_id = '"+teamid+"';"

    with connection.cursor() as cursor:
        cursor.execute(query)
        puntajes = dictfetchall(cursor)

    for puntaje in list(puntajes):
        puntajeDeEquipo += puntaje['pers_score']
    equipo.team_effectiveness = puntajeDeEquipo/len(puntajes)

    equipo.save()

def equiposDePersona(personId):
    query= "select tp.*, equipo.*, persona.pers_name, persona.pers_lastname \
            from opx.team_person as tp \
            inner join opx.team as equipo on equipo.team_id = tp.team_id \
            inner join opx.person as persona on persona.pers_id = tp.person_id \
            where tp.person_id = '"+personId+"';"
    with connection.cursor() as cursor:
        cursor.execute(query)
        equiposP = dictfetchall(cursor)
    
    return equiposP

##
# @brief Función que calcula el estado actual de un proyecto. provee datos como:
# Avance de la ejecución
# Avance de la validación
# Cantidad de integrantes
# @param proyid Identificación del proyecto
# @return Diccionario
#
def reporteEstadoProyecto(proyid):

    query = "select count(distinct tp.person_id) from opx.team_person as tp inner join opx.project_team as pt on tp.team_id = pt.team_id where pt.project_id = '"+proyid+"';"
    with connection.cursor() as cursor:
        cursor.execute(query)
        cantidadMiembros = dictfetchall(cursor)

    return {
        'estado-validacion':    0,
        'cantidad-integrantes': cantidadMiembros
    }

def reporteEstadoTarea(tarea):

    if tarea['taretipo'] == 1:
        encuestas = models.Encuesta.objects.filter(tareid__exact=tarea['tareid'])
        progreso = (len(encuestas) * 100) / tarea['tarerestriccant']

    return progreso