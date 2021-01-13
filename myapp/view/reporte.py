
from django.db import (connection, transaction)
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from myapp.view.utilidades import dictfetchall
from django.http.response import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from myapp import models

##
# @brief 
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def reporteEquiposView(request):
    return render(request, "reportes/reporte-equipo.html")


def miembrosEquipoView(request, planid):

    try:
        plantilla = models.Team.objects.get(pk=planid)

        response = render(request, "reportes/reportes-miembros.html", {'plantilla': plantilla})

    except ObjectDoesNotExist:
        response = HttpResponse("", status=404)

    except ValidationError:
        response = HttpResponse("", status=400)

    return response

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def canva1(request):

    query = "select genero.gender_name, count(*) \
            from opx.gender as genero \
            inner join opx.person as persona on persona.gender_id = genero.gender_id \
            where persona.isactive = 1 \
            group by genero.gender_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': resultados,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def canva2(request):

    query = "select rol.role_name, count(*) \
            from opx.role as rol \
            inner join opx.person as persona on persona.role_id = rol.role_id \
            where persona.isactive = 1 \
            group by rol.role_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': resultados,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def canva3(request):

    query = "select nivelE.educlevel_name, count(*) \
            from opx.education_level as nivelE \
            inner join opx.person as persona on persona.education_level_id = nivelE.educlevel_id \
            where persona.isactive = 1 \
            group by nivelE.educlevel_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': resultados,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def generales(request):
    
    with connection.cursor() as cursor:
        usuarios = "select count(*) as cantidad from opx.person" 
        cursor.execute(usuarios)
        usuarios = dictfetchall(cursor)[0]['cantidad']

        decisiones = "select count(*) as cantidad from opx.decision" 
        cursor.execute(decisiones)
        decisiones = dictfetchall(cursor)[0]['cantidad']

        contextos = "select count(*) as cantidad from opx.context" 
        cursor.execute(contextos)
        contextos = dictfetchall(cursor)[0]['cantidad']

        instrumentos = "select count(*) as cantidad from opx.instrument" 
        cursor.execute(instrumentos)
        instrumentos = dictfetchall(cursor)[0]['cantidad']

        proyectos = "select count(*) as cantidad from opx.project" 
        cursor.execute(proyectos)
        proyectos = dictfetchall(cursor)[0]['cantidad']

        tareas = "select count(*) as cantidad from opx.task" 
        cursor.execute(tareas)
        tareas = dictfetchall(cursor)[0]['cantidad']

        equipos = "select count(*) as cantidad from opx.team" 
        cursor.execute(equipos)
        equipos = dictfetchall(cursor)[0]['cantidad']

    response = {
        'code': 200,
        'data': {
            'usuarios': usuarios,
            'decisiones': decisiones,
            'contextos': contextos,
            'instrumentos': instrumentos,
            'proyectos': proyectos,
            'tareas': tareas,
            'equipos': equipos
        },
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def proyectosPersona(request, personId):
    
    query = "select * \
            from (select tk.*, count(su.survery_id) \
            from opx.survery as su \
            inner join opx.task as tk on tk.task_id = su.task_id \
            inner join opx.task_priority as prio on prio.priority_id = tk.task_priority_id \
            where su.person_id = '"+personId+"' group by tk.task_id) as taskcount \
            inner join opx.task_priority as tprio on taskcount.task_priority_id = tprio.priority_id \
            inner join opx.project as proy on proy.proj_id = taskcount.project_id \
            inner join opx.task_restriction as rest on rest.restriction_id = taskcount.task_restriction_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        proyectosP = dictfetchall(cursor)

        for proyectP in proyectosP:
            cantidadEncuestas = proyectP['count']
            prioridadEncuestas = proyectP['priority_number']
            prueba = cantidadEncuestas*prioridadEncuestas
            proyectP['participation'] = prueba
            

    response = {
        'code': 200,
        'data': proyectosP,
        'status': 'success'
    }
    return JsonResponse(response, safe=False, status=response['code'])


##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def equiposPersona(request, personId):
    
    query= "select tp.*, equipo.*, persona.pers_name, persona.pers_lastname, persona.pers_score \
            from opx.team_person as tp \
            inner join opx.team as equipo on equipo.team_id = tp.team_id \
            inner join opx.person as persona on persona.pers_id = tp.person_id \
            where tp.person_id = '"+personId+"';"

    with connection.cursor() as cursor:
        cursor.execute(query)
        equiposP = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': equiposP,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])


##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
def reporteMiembroView(request, personId):

    try:
        persona = models.Person.objects.get(pk=personId)

        response = render(request, "reportes/reporteIndividualMiembro.html")

    except ObjectDoesNotExist:
        response = HttpResponse("", status=404)

    except ValidationError:
        response = HttpResponse("", status=400)

    return response

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def detallePersona(request, personId):
    
    query= "select persona.*, usuario.useremail, nivelE.educlevel_name, genero.gender_name, barrio.neighb_name, rol.role_name \
            from opx.person as persona \
            inner join opx.user as usuario on persona.user_id = usuario.userid \
            inner join opx.education_level as nivelE on nivelE.educlevel_id = persona.education_level_id \
            inner join opx.gender as genero on genero.gender_id = persona.gender_id \
            inner join opx.neighborhood as barrio on barrio.neighb_id = persona.neighborhood_id \
            inner join opx.role as rol on rol.role_id = persona.role_id \
            where persona.pers_id = '"+personId+"';"

    with connection.cursor() as cursor:
        cursor.execute(query)
        detalle = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': detalle[0],
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee el ranking de usuarios del sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def ranking(request):
    try:
        inicio = request.GET.get('inicio')
        fin = request.GET.get('fin')

        query = "select persona.pers_name, persona.pers_lastname, persona.pers_score \
                from opx.person as persona  \
                where (persona.role_id = '53ad3141-56bb-4ee2-adcf-5664ba03ad65' or persona.role_id = '0be58d4e-6735-481a-8740-739a73c3be86' or persona.role_id = '628acd70-f86f-4449-af06-ab36144d9d6a') and persona.pers_score>0 \
                order by persona.pers_score DESC limit 30"

        with connection.cursor() as cursor:
            cursor.execute(query)
            rank = dictfetchall(cursor)

            i = 1
            for r in rank:
                r['clasificacion'] = i
                i=i+1

        response = {
            'code': 200,
            'data': list(rank)[int(inicio):int(fin)],
            'status': 'success'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

    ##
# @brief 
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def reporteRankView(request):
    return render(request, "reportes/reporteRank.html")