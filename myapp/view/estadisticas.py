from datetime import date
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import connection
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp.models import Proyecto, Rol, Usuario, Tarea, Instrumento, Encuesta, NivelEducativo, Barrio, Equipo, ContextoProyecto, DecisionProyecto, DelimitacionGeografica
from myapp.view.utilidades import dictfetchall, reporteEstadoProyecto, reporteEstadoTarea
from myapp.views import detalleFormularioKoboToolbox

import csv
import json
import os

# ==================== Antes ===================

##
# @brief Recurso que provee estadisticas generales del sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def datosGenerales(request):

    with connection.cursor() as cursor:

        cantidadUsuarios = "SELECT count(*) as cantidad from v1.usuarios;"
        cursor.execute(cantidadUsuarios)
        cantidadUsuarios = dictfetchall(cursor)[0]['cantidad']

        cantidadDecisiones = "SELECT count(*) as cantidad from v1.decisiones;"
        cursor.execute(cantidadDecisiones)
        cantidadDecisiones = dictfetchall(cursor)[0]['cantidad']

        cantidadContextos = "SELECT count(*) as cantidad from v1.contextos;"
        cursor.execute(cantidadContextos)
        cantidadContextos = dictfetchall(cursor)[0]['cantidad']

        cantidadProyectos = "SELECT count(*) as cantidad from v1.proyectos;"
        cursor.execute(cantidadProyectos)
        cantidadProyectos = dictfetchall(cursor)[0]['cantidad']

        cantidadTareas = "SELECT count(*) as cantidad from v1.tareas;"
        cursor.execute(cantidadTareas)
        cantidadTareas = dictfetchall(cursor)[0]['cantidad']

    response = {
        'code': 200,
        'data': {
            'usuarios': cantidadUsuarios,
            'decisiones': cantidadDecisiones,
            'contextos': cantidadContextos,
            'proyectos': cantidadProyectos,
            'tareas': cantidadTareas
        },
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios Por Rol del Sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXRol(request):

    roles = Rol.objects.all()

    data = {
        'roles': [],
        'cantidadUsuarios': []
    }

    for rol in roles:

        with connection.cursor() as cursor:

            query = "SELECT count(*) as cantidad from v1.usuarios where rolid = '" + str(rol.rolid) + "';"
            cursor.execute(query)

            data['roles'].append(rol.rolname)
            data['cantidadUsuarios'].append(dictfetchall(cursor)[0]['cantidad'])

    response = {
         'code': 200,
         'data': data,
         'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios Por Sexo del Sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXGenero(request):

    generos = [
        {
            'label': 'Masculino',
            'value': '0634cdce-f7c6-405a-8a14-9a9973ef81a9'
        },
        {
            'label': 'Femenino',
            'value': '9fc690cc-dc94-4df4-a58b-245135b059ec'
        }
    ]

    data = {
        'generos': [],
        'cantidad': []
    }

    for genero in generos:

        with connection.cursor() as cursor:

             query = "SELECT count(*) as cantidad from v1.usuarios where generoid = '{}';" \
                     .format(genero['value'])

             cursor.execute(query)

             data['generos'].append(genero['label'])
             data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

    response = {
         'code': 200,
         'data': data,
         'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios Por Nivel Educativo del Sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXNivelEducativo(request):

    nivelesEducativos = NivelEducativo.objects.all()

    data = {
        'niveles_educativos': [],
        'cantidad': []
    }

    for nv in nivelesEducativos:
        with connection.cursor() as cursor:
            query = "SELECT count(*) as cantidad from v1.usuarios where nivel_educativo_id = '{}';" \
                    .format(nv.nivelid)

            cursor.execute(query)

            data['niveles_educativos'].append(nv.nombre)
            data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios Por Barrio del Sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXBarrio(request):

    barrios = Barrio.objects.all()

    data = {
        'barrios': [],
        'cantidad': []
    }

    for b in barrios:
        with connection.cursor() as cursor:
            query = "SELECT count(*) as cantidad from v1.usuarios where barrioid = {};" \
                    .format(b.barrioid)

            cursor.execute(query)

            cantidad = dictfetchall(cursor)[0]['cantidad']

            if cantidad > 0:

                data['barrios'].append(b.nombre)
                data['cantidad'].append(cantidad)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de tareas Por Tipo del Sistema
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def tareasXTipo(request):

    tiposTarea = [
        {
            'label': 'Encuesta',
            'value': '1'
        },
        {
            'label': 'Cartografia',
            'value': '2'
        }
    ]

    data = {
        'tipos': [],
        'cantidad': []
    }

    for tipo in tiposTarea:

        with connection.cursor() as cursor:

             query = "SELECT count(*) as cantidad from v1.tareas where taretipo = {}" \
                     .format(tipo['value'])

             cursor.execute(query)

             data['tipos'].append(tipo['label'])
             data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

    response = {
         'code': 200,
         'data': data,
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

    usuarios = Usuario.objects \
               .order_by('-puntaje') \
               .values('userfullname', 'puntaje')

    response = {
        'code': 200,
        'data': list(usuarios)[0:3],
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

# ==================== Durante ============================

##
# @brief Recurso que provee los proyectos y tareas del sistema que se encuentran en ejecucion
# con el fin de mostrarlos en un diagrama de Gantt
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def proyectosTareas(request):

    #proyectos = Proyecto.objects.all()

    with connection.cursor() as cursor:

        fechaActual = date.today().strftime("%Y-%m-%d")

        query = "SELECT p.proyid, p.proynombre, p.proydescripcion, proyfechacreacion, p.proyfechacierre from v1.proyectos as p " \
                "WHERE p.proyfechacreacion <=  '{0} 23:59:59' " \
                "AND p.proyfechacierre >= '{0}'" \
                .format(fechaActual)

        cursor.execute(query)

        proyectos = dictfetchall(cursor)

    data = []
    project = {}
    tareasProyecto = []
    progresoProyecto = 0

    for proyecto in proyectos:
        progresoProyecto = 0
        tareasProyecto = []

        project = {
            'id': proyecto['proyid'],
            'name': proyecto['proynombre'],
            'start': proyecto['proyfechacreacion'],
            'end': proyecto['proyfechacierre'],
            'dependencies': '',
            'type': 'project'
        }

        tareas = Tarea.objects.filter(proyid__exact=proyecto['proyid'])

        for tarea in tareas:

            if tarea.taretipo == 1:

                task = {
                    'id': tarea.tareid,
                    'name': tarea.tarenombre,
                    'start': proyecto['proyfechacreacion'],
                    'end': proyecto['proyfechacierre'],
                    'dependencies': proyecto['proyid'],
                    'type': 'task'
                }

                encuestas = Encuesta.objects.filter(tareid__exact=tarea.tareid)
                progreso = (len(encuestas) * 100) / tarea.tarerestriccant
                task['progress'] = progreso
                tareasProyecto.append(task)

                progresoProyecto = progresoProyecto + progreso


        if progresoProyecto > 0:
            progresoProyecto = (progresoProyecto * 100) / (len(tareas) * 100)

        project['progress'] = progresoProyecto

        data.append(project)
        data.extend(tareasProyecto)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee informacion correspondiente al estado actual de los proyectos que se encuentran en
# ejecución. Provee datos como:
# avance de ejecución
# avance de validacion
# cantidad de integrantes
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def estadoActualProyectos(request):

    with connection.cursor() as cursor:

        fechaActual = date.today().strftime("%Y-%m-%d")

        query = "SELECT p.proyid, p.proynombre, p.proydescripcion, proyfechacreacion, u.userfullname from v1.proyectos as p " \
                "INNER JOIN v1.usuarios as u ON u.userid = p.proypropietario " \
                "WHERE p.proyfechacreacion <=  '{0} 23:59:59' " \
                "AND p.proyfechacierre >= '{0}'" \
                .format(fechaActual)

        cursor.execute(query)

        proyectos = dictfetchall(cursor)
        data = []

    for p in proyectos:

        estadoProyecto = reporteEstadoProyecto(p['proyid'])

        proyecto = {
            'id':           p['proyid'],
            'nombre':       p['proynombre'],
            'descripcion':  p['proydescripcion'],
            'fecha':        p['proyfechacreacion'],
            'encargado':    p['userfullname'],
            'integrantes':  estadoProyecto['cantidad-integrantes'],
            'progreso':     estadoProyecto['progreso-proyecto'],
            'validacion':   estadoProyecto['estado-validacion']
        }

        data.append(proyecto)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

# ===================== Después ===========================

##
# @brief Recurso que provee los proyectos y tareas del sistema que se encuentran terminados
# con el fin de mostrarlos en un diagrama de Gantt
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def proyectosTareasVencidos(request):

    #proyectos = Proyecto.objects.all()

    with connection.cursor() as cursor:

        fechaActual = date.today().strftime("%Y-%m-%d")

        query = "SELECT p.proyid, p.proynombre, p.proydescripcion, proyfechacreacion, p.proyfechacierre from v1.proyectos as p " \
                "WHERE p.proyfechacreacion <=  '{0} 23:59:59' " \
                "AND p.proyfechacierre <= '{0}'" \
                .format(fechaActual)

        cursor.execute(query)

        proyectos = dictfetchall(cursor)

    data = []
    project = {}
    tareasProyecto = []
    progresoProyecto = 0

    for proyecto in proyectos:
        progresoProyecto = 0
        tareasProyecto = []

        project = {
            'id': proyecto['proyid'],
            'name': proyecto['proynombre'],
            'start': proyecto['proyfechacreacion'],
            'end': proyecto['proyfechacierre'],
            'dependencies': '',
            'type': 'project'
        }

        tareas = Tarea.objects.filter(proyid__exact=proyecto['proyid'])

        for tarea in tareas:

            if tarea.taretipo == 1:

                task = {
                    'id': tarea.tareid,
                    'name': tarea.tarenombre,
                    'start': proyecto['proyfechacreacion'],
                    'end': proyecto['proyfechacierre'],
                    'dependencies': proyecto['proyid'],
                    'type': 'task'
                }

                encuestas = Encuesta.objects.filter(tareid__exact=tarea.tareid)
                progreso = (len(encuestas) * 100) / tarea.tarerestriccant
                task['progress'] = progreso
                tareasProyecto.append(task)

                progresoProyecto = progresoProyecto + progreso


        if progresoProyecto > 0:
            progresoProyecto = (progresoProyecto * 100) / (len(tareas) * 100)

        project['progress'] = progresoProyecto

        data.append(project)
        data.extend(tareasProyecto)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee informacion correspondiente al estado actual de los proyectos que se encuentran
# terminados. Provee datos como:
# avance de ejecución
# avance de validacion
# cantidad de integrantes
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def estadoActualProyectosVencidos(request):

    with connection.cursor() as cursor:

        fechaActual = date.today().strftime("%Y-%m-%d")

        query = "SELECT p.proyid, p.proynombre, p.proydescripcion, proyfechacreacion, u.userfullname from v1.proyectos as p " \
                "INNER JOIN v1.usuarios as u ON u.userid = p.proypropietario " \
                "WHERE p.proyfechacreacion <=  '{0} 23:59:59' " \
                "AND p.proyfechacierre <= '{0}'" \
                .format(fechaActual)

        cursor.execute(query)

        proyectos = dictfetchall(cursor)
        progresoProyecto = 0
        data = []

    for p in proyectos:
        estadoProyecto = reporteEstadoProyecto(p['proyid'])

        proyecto = {
            'id': p['proyid'],
            'nombre': p['proynombre'],
            'descripcion': p['proydescripcion'],
            'fecha': p['proyfechacreacion'],
            'encargado': p['userfullname'],
            'integrantes': estadoProyecto['cantidad-integrantes'],
            'progreso': estadoProyecto['progreso-proyecto'],
            'validacion': estadoProyecto['estado-validacion']
        }

        data.append(proyecto)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

# ==================== Detalle Proyecto =======================

##
# @brief Recurso que provee la cantidad de tareas por tipo de un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def tareasXTipoProyecto(request, proyid):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        tiposTarea = [
            {
                'label': 'Encuesta',
                'value': '1'
            },
            {
                'label': 'Cartografia',
                'value': '2'
            }
        ]

        data = {
            'tipos': [],
            'cantidad': []
        }

        for tipo in tiposTarea:

            with connection.cursor() as cursor:

                 query = "SELECT count(*) as cantidad from v1.tareas where taretipo = {} and proyid = '{}'" \
                         .format(tipo['value'], proyid)

                 cursor.execute(query)

                 data['tipos'].append(tipo['label'])
                 data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

        response = {
             'code': 200,
             'data': data,
             'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de tareas por estado de un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def tareasXEstadoProyecto(request, proyid):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        tiposTarea = [
            {
                'label': 'En progreso',
                'value': '0'
            },
            {
                'label': 'Terminada',
                'value': '1'
            },
            {
                'label': 'Validada',
                'value': '2'
            }
        ]

        data = {
            'estados': [],
            'cantidad': []
        }

        for tipo in tiposTarea:

            with connection.cursor() as cursor:

                 query = "SELECT count(*) as cantidad from v1.tareas where tareestado = {} and proyid = '{}'" \
                         .format(tipo['value'], proyid)

                 cursor.execute(query)

                 data['estados'].append(tipo['label'])
                 data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

        response = {
            'code': 200,
            'data': data,
            'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios por rol de un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXRolProyecto(request, proyid):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        roles = Rol.objects.all()

        data = {
            'roles': [],
            'cantidad': []
        }

        for rol in roles:

            with connection.cursor() as cursor:

                query = "SELECT count(*) as cantidad from v1.equipos as e " \
                        "INNER JOIN v1.usuarios as u ON u.userid = e.userid " \
                        "where u.rolid = '{}' " \
                        "AND e.proyid = '{}';" \
                        .format(str(rol.rolid), str(proyid))

                print(query)

                cursor.execute(query)

                data['roles'].append(rol.rolname)
                data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

        response = {
             'code': 200,
             'data': data,
             'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios por barrio de un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXBarrioProyecto(request, proyid):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        barrios = Barrio.objects.all()

        data = {
            'barrios': [],
            'cantidad': []
        }

        for b in barrios:
            with connection.cursor() as cursor:
                query = "SELECT count(*) as cantidad from v1.equipos as e " \
                        "INNER JOIN v1.usuarios as u ON u.userid = e.userid " \
                        "where u.barrioid = {} " \
                        "AND e.proyid = '{}'" \
                        .format(b.barrioid, str(proyid))

                cursor.execute(query)

                cantidad = dictfetchall(cursor)[0]['cantidad']

                if cantidad > 0:

                    data['barrios'].append(b.nombre)
                    data['cantidad'].append(cantidad)

        response = {
            'code': 200,
            'data': data,
            'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios por sexo de un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXGeneroProyecto(request, proyid):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        generos = [
            {
                'label': 'Masculino',
                'value': '0634cdce-f7c6-405a-8a14-9a9973ef81a9'
            },
            {
                'label': 'Femenino',
                'value': '9fc690cc-dc94-4df4-a58b-245135b059ec'
            }
        ]

        data = {
            'generos': [],
            'cantidad': []
        }

        for genero in generos:

            with connection.cursor() as cursor:

                 query = "SELECT count(*) as cantidad from v1.equipos as e " \
                         "INNER JOIN v1.usuarios as u ON u.userid = e.userid " \
                         "where u.generoid = '{}' " \
                         "AND e.proyid = '{}';" \
                         .format(genero['value'], str(proyid))

                 cursor.execute(query)

                 data['generos'].append(genero['label'])
                 data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

        response = {
             'code': 200,
             'data': data,
             'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee la cantidad de usuarios por nivel educativo de un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXNivelEducativoProyecto(request, proyid):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        nivelesEducativos = NivelEducativo.objects.all()

        data = {
            'niveles_educativos': [],
            'cantidad': []
        }

        for nv in nivelesEducativos:
            with connection.cursor() as cursor:
                query = "SELECT count(*) as cantidad from v1.equipos as e " \
                        "INNER JOIN v1.usuarios as u ON u.userid = e.userid " \
                        "where u.nivel_educativo_id = '{}' " \
                        "AND e.proyid = '{}';" \
                        .format(nv.nivelid, str(proyid))

                cursor.execute(query)

                data['niveles_educativos'].append(nv.nombre)
                data['cantidad'].append(dictfetchall(cursor)[0]['cantidad'])

        response = {
            'code': 200,
            'data': data,
            'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee datos especificos de un proyecto. Tales como:
# Cantidad de decisiones
# Cantidad de Contexto
# Cantidad de Campañas
# Su convocatoria
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def datosGeneralesProyecto(request, proyid):

    try:
        proyecto = Proyecto.objects.get(pk=proyid)

        contextos = len(ContextoProyecto.objects.filter(proyid__exact=proyid))
        decisiones = len(DecisionProyecto.objects.filter(proyid__exact=proyid))
        campanas = len(Tarea.objects.filter(proyid__exact=proyid))
        convocatoria = len(Equipo.objects.filter(proyid__exact=proyid))

        response = {
            'code': 200,
            'data': {
                'contextos':    contextos,
                'decisiones':   decisiones,
                'campana':      campanas,
                'convocatoria': convocatoria
            },
            'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee un archivo que contiene las encuestas realizadas en un proyecto
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def exportarDatos(request, proyid):

    try:
        proyecto = Proyecto.objects.get(pk=proyid)

        tareas = Tarea.objects.filter(proyid__exact=proyid)

        encuestas = []

        for t in tareas:
            encuestasTarea = Encuesta.objects.filter(tareid__exact=t.tareid)

            for e in encuestasTarea:

                contenido = json.loads(e.contenido)
                del contenido['_geolocation']
                encuestas.append(contenido)

        if len(encuestas) > 0:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="informacion.csv"'

            writer = csv.writer(response)
            writer.writerow(encuestas[0].keys())

            for e in encuestas:
                row = [v for v in e.values()]
                writer.writerow(row)

        else:
            raise ObjectDoesNotExist("")

    except ObjectDoesNotExist:
        response = HttpResponse("", status=404)

    except ValidationError:
        response = HttpResponse("", status=400)

    return response

@api_view(['GET'])
@permission_classes((AllowAny,))
def exportarDatosProyecto(request, proyid):
    try:
        proyecto = Proyecto.objects.get(pk=proyid)

        contextos = len(ContextoProyecto.objects.filter(proyid__exact=proyid))
        decisiones = len(DecisionProyecto.objects.filter(proyid__exact=proyid))
        campanas = len(Tarea.objects.filter(proyid__exact=proyid))
        convocatoria = len(Equipo.objects.filter(proyid__exact=proyid))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informacion.csv"'

        writer = csv.writer(response)
        writer.writerow(['Campo', 'Valor'])
        writer.writerow(['Nombre Proyecto', proyecto.proynombre])
        writer.writerow(['Fecha de Inicio', proyecto.proyfechainicio])
        writer.writerow(['Fecha de Cierre', proyecto.proyfechacierre])
        writer.writerow(['Contextos', contextos])
        writer.writerow(['decisiones', decisiones])
        writer.writerow(['Campañas', campanas])
        writer.writerow(['Convocatoria', convocatoria])

    except ObjectDoesNotExist:
        response = HttpResponse("", status=404)

    except ValidationError:
        response = HttpResponse("", status=400)

    return response

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def rankingPorProyecto(request, proyid):

    try:
        # Verificación de existencia de proyecto
        Proyecto.objects.get(pk = proyid)

        # Lista que recibe IDS de usuarios
        equipo = []

        # Consulta de equipo de proyecto
        queryEquipo = Equipo.objects.filter(proyid = proyid)

        # Inserción de los identificadores en la lista equipo
        for q in queryEquipo:
            equipo.append(q.userid)

        # Consulta de usuarios que hacen parte del equipo
        usuarios = Usuario.objects \
                   .filter(pk__in = equipo) \
                   .order_by('-puntaje') \
                   .values('userfullname', 'puntaje')

        response = {
            'code': 200,
            'data': list(usuarios)[0:3],
            'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'message':  'Proyecto inexistente'
        }

    except ValidationError:
        response = {
            'code':     400,
            'message':  'Proyecto inexistente'
        }

    return JsonResponse(response, safe=False, status=response['code'])

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dimensionesProyecto(request, proyid):

    try:
        # Validación de Existencia de proyecto
        Proyecto.objects.get(pk = proyid)

        # Consulta de las dimensiones del proyecto
        dimensiones = DelimitacionGeografica \
                      .objects \
                      .filter(proyid = proyid) \
                      .values('dimensionid', 'nombre')

        response = {
            'code':         200,
            'dimensiones':  list(dimensiones),
            'status':       'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'status':   'error'
        }

    except ValidationError:
        response = {
            'code':     400,
            'status':   'error'
        }

    return JsonResponse(response, safe = False, status = response['code'])

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def tareasDimensionProyecto(request, dimensionid):

    try:
        DelimitacionGeografica.objects.get(pk = dimensionid)

        tareas = Tarea \
                 .objects \
                 .filter(dimensionid=dimensionid) \
                 .values('tareid', 'tarenombre', 'taretipo', 'tarerestriccant')

        for tarea in tareas:
            tarea['progreso'] = reporteEstadoTarea(tarea)

        response = {
            'code':     200,
            'tareas':   list(tareas),
            'status':   'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'status':   'error'
        }

    except ValidationError:
        response = {
            'code':     400,
            'status':   'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def instrumentosProyecto(request, proyid):

    try:
        Proyecto.objects.get(pk=proyid)

        with connection.cursor() as cursor:

            query = "SELECT DISTINCT ON (t.instrid) \
                    t.instrid, i.instrnombre, i.instrtipo \
                    FROM v1.tareas as t \
                    INNER JOIN v1.instrumentos as i ON i.instrid = t.instrid"

            cursor.execute(query)

            # Formato de resultado de consulta
            instrumentos = dictfetchall(cursor)

        # Cantidad de Encuestas
        encuestas = 0

        # Cantidad de Cartografias
        cartografias = 0

        for instr in instrumentos:
            if instr['instrtipo'] == 1:
                encuestas = encuestas + 1
            elif instr['instrtipo'] == 2:
                cartografias = cartografias + 1

        response = {
            'code':         200,
            'stats': {
                'tipos':    ['encuesta', 'cartografia'],
                'cantidad': [encuestas, cartografias]
            },
            'status':   'success'
        }
    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'status':   'error'
        }

    except ValidationError:
        response = {
            'code':     400,
            'status':   'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def usuariosXBarrioEspecifico(request, proyid, keyword):

    try:

        proyecto = Proyecto.objects.get(pk=proyid)

        # Consulta del barrio en base al nombre proveido
        barrio = Barrio.objects.get(nombre=keyword)

        # Consulta de usuarios
        with connection.cursor() as cursor:
            query = "SELECT u.userfullname from v1.equipos as e " \
                    "INNER JOIN v1.usuarios as u ON u.userid = e.userid " \
                    "where u.barrioid = {} " \
                    "AND e.proyid = '{}'" \
                .format(barrio.barrioid, str(proyid))

            cursor.execute(query)

            usuarios = dictfetchall(cursor)

        response = {
            'code':     200,
            'usuarios': usuarios,
            'status':   'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'status':   'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Script de ejemplo  que tiene la capacidad de darle formato un archivo de encuestas generado por el sistema
# @param request instancia HttpRequest
# @param proyid Identificación del Proyecto
# @return cadena JSON
#
def limpiezaDatos(request, proyid):

    camposDescarte = [
        '_notes',
        '_bamboo_dataset_id',
        '_tags',
        '_xform_id_string',
        'meta/instanceID',
        '_version_',
        '_status',
        '__version__',
        '_validation_status',
        '_uuid',
        '_submitted_by',
        'formhub / uuid',
        'formhub/uuid',
        '_id',
        '_geolocation'
    ]

    columnasDescarte = []
    contenidoFormateado = []

    # Especificando ubicación del archivo
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'myapp/static/informacion.csv')

    # Abriendo el archivo en modo lectura
    file = open(file_path, "r")

    if file.mode == "r":
        content = file.read()

        lines = content.splitlines()

        campos = lines[0].split(',')

        # Obtener posición de columnas a descartar
        for i, c in enumerate(campos):

            for cd in camposDescarte:

                if c == cd:
                    columnasDescarte.append(i)

        # Obtener los Datos de Interés
        for line in lines:

            fila = line.split(',')
            data = []

            for i, d in enumerate(fila):

                coincidencias = 0

                for c in columnasDescarte:

                    if i == c:
                        coincidencias += 1

                if coincidencias == 0:
                    data.append(d)

            contenidoFormateado.append(data)

    #print(contenidoFormateado)

    csvFile = io.StringIO()
    writer = csv.writer(csvFile)

    for cf in contenidoFormateado:
        writer.writerow(cf)

    print(csvFile.getValue())

# ================ Vistas ===============

##
# @brief Plantilla de estadisticas generales del sistema
# @param request instancia HttpRequest
# @return plantilla HTML
#
def estadisticasView(request):

    return render(request, "reportes/antes.html")

##
# @brief Plantilla de estadisticas correspondiente a los proyectos que se encuentran en ejecución
# @param request instancia HttpRequest
# @return plantilla HTML
#
def estadisticasDuranteView(request):

    return render(request, "reportes/durante.html")

##
# @brief Plantilla de estadisticas correspondiente a los proyectos que se encuentran terminados
# @param request instancia HttpRequest
# @return plantilla HTML
#
def estadisticasDespuesView(request):

    return render(request, "reportes/despues.html")

##
# @brief Plantilla de estadisticas correspondiente a un proyecto especifico
# @param request instancia HttpRequest
# @param proyid Identificación de un proyecto
# @return plantilla HTML
#
def estadisticasDetalleView(request, proyid):

    try:
        proyecto = Proyecto.objects.get(pk=proyid)

        return render(request, "reportes/detalle.html", {'proyecto': proyecto})

    except ObjectDoesNotExist:
        response = HttpResponse("", status=404)

    except ValidationError:
        response = HttpResponse("", status=400)


    return response

##
# @brief Plantilla de estadisticas correspondiente al ranking global de los usuarios
# @param request instancia HttpRequest
# @return plantilla HTML
#
def rankingView(request):

    return render(request, "reportes/rank2.html")

##
# @brief Plantilla de estadisticas correspondiente a los reportes generales de todos los proyectos
# @param request instancia HttpRequest
# @return plantilla HTML
#
def reportesProyectosGeneralesView(request):

    return render(request, "reportes/reportesProyectosGenerales.html")


##
# @brief Plantilla de estadisticas correspondiente al reporte individual de cada proyecto
# @param request instancia HttpRequest
# @return plantilla HTML
#
def reportesProyectosIndividualesView(request):

    return render(request, "reportes/reportesProyectosIndividuales.html")