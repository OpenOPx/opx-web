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

from myapp.models import Proyecto, Rol, Usuario, Tarea, Instrumento, Encuesta, NivelEducativo, Barrio, Equipo
from myapp.view.utilidades import dictfetchall
from myapp.views import detalleFormularioKoboToolbox

# ==================== Antes ===================

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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def ranking(request):

    usuarios = Usuario.objects.order_by('-puntaje').values()

    response = {
        'code': 200,
        'data': list(usuarios)[0:3],
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

# ==================== Durante ============================

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
        progresoProyecto = 0
        data = []

    for p in proyectos:

        progresoProyecto = 0
        tareas = Tarea.objects.filter(proyid__exact=p['proyid'])
        tareasValidadas = 0

        for tarea in tareas:

            if tarea.taretipo == 1:

                encuestas = Encuesta.objects.filter(tareid__exact=tarea.tareid)
                progreso = (len(encuestas) * 100) / tarea.tarerestriccant

                progresoProyecto = progresoProyecto + progreso

            if tarea.tareestado == 2:
                tareasValidadas += 1

        if progresoProyecto > 0:
            progresoProyecto = (progresoProyecto * 100) / (len(tareas) * 100)

        if(len(tareas) > 0):
            estadoValidacion = (tareasValidadas * 100) / len(tareas)
        else:
            estadoValidacion = 0

        proyecto = {
            'id': p['proyid'],
            'nombre': p['proynombre'],
            'descripcion': p['proydescripcion'],
            'fecha': p['proyfechacreacion'],
            'encargado': p['userfullname'],
            'integrantes': len(Equipo.objects.filter(proyid__exact=p['proyid'])),
            'progreso': progresoProyecto,
            'validacion': estadoValidacion
        }

        data.append(proyecto)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

# ===================== Después ===========================

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

        progresoProyecto = 0
        tareas = Tarea.objects.filter(proyid__exact=p['proyid'])
        tareasValidadas = 0

        for tarea in tareas:

            if tarea.taretipo == 1:

                encuestas = Encuesta.objects.filter(tareid__exact=tarea.tareid)
                progreso = (len(encuestas) * 100) / tarea.tarerestriccant

                progresoProyecto = progresoProyecto + progreso

            if tarea.tareestado == 2:
                tareasValidadas += 1

        if progresoProyecto > 0:
            progresoProyecto = (progresoProyecto * 100) / (len(tareas) * 100)

        if(len(tareas) > 0):
            estadoValidacion = (tareasValidadas * 100) / len(tareas)
        else:
            estadoValidacion = 0

        proyecto = {
            'id': p['proyid'],
            'nombre': p['proynombre'],
            'descripcion': p['proydescripcion'],
            'fecha': p['proyfechacreacion'],
            'encargado': p['userfullname'],
            'integrantes': len(Equipo.objects.filter(proyid__exact=p['proyid'])),
            'progreso': progresoProyecto,
            'validacion': estadoValidacion
        }

        data.append(proyecto)

    response = {
        'code': 200,
        'data': data,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

# ==================== Detalle Proyecto =======================

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

# ================ Vistas ===============
def estadisticasView(request):

    return render(request, "reportes/antes.html")

def estadisticasDuranteView(request):

    return render(request, "reportes/durante.html")


