from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import(
    Paginator,
    EmptyPage
)
from django.db import (connection, transaction)
from django.db.utils import IntegrityError, DataError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp import models
from myapp.view.utilidades import dictfetchall
from myapp.views import detalleFormularioKoboToolbox

# ============================= Proyectos ========================

@api_view(["GET"])
@permission_classes((AllowAny,))
def listadoProyectos(request):

    search = request.GET.get('search')
    page = request.GET.get('page')
    all = request.GET.get('all')

    try:

        if request.META['HTTP_AUTHORIZATION'] != 'null':

            # Decodificando el access token
            tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                        settings.SIMPLE_JWT['VERIFYING_KEY'])
            tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
            #consultando el usuario
            user = models.Usuario.objects.get(pk = tokenDecoded['user_id'])

            # ============================ Consultando proyectos ====================================

            #Consulta de proyectos para super administrador
            if str(user.rolid) == '8945979e-8ca5-481e-92a2-219dd42ae9fc':
                proyectos = models.Proyecto.objects.all()

            # Consulta de proyectos para proyectista
            elif str(user.rolid) == '628acd70-f86f-4449-af06-ab36144d9d6a':
                proyectos = models.Proyecto.objects.filter(proypropietario__exact = user.userid)

            # Consulta de proyectos para voluntarios
            elif str(user.rolid) == '0be58d4e-6735-481a-8740-739a73c3be86':

                proyectosAsignados = models.Equipo.objects.filter(userid__exact = user.userid)
                proyectosAsignadosID = []

                for p in proyectosAsignados:
                    proyectosAsignadosID.append(p.proyid)

                proyectos = models.Proyecto.objects.filter(pk__in = proyectosAsignadosID)

            #Tipo de usuario distinto
            else:
                proyectos = models.Proyecto.objects.filter(proynombre = 'qwerty')

        # Usuario Invitado
        else:
            proyectos = models.Proyecto.objects.all()

        # ================= Busqueda de proyectos
        if search:
            proyectos = proyectos.filter(proynombre__icontains = search)

        # Especificando orden
        proyectos = proyectos.order_by('-proyfechacreacion')

        # convirtiendo a lista de diccionarios
        proyectos = list(proyectos.values())

        listadoProyectos = []
        for p in proyectos:

            #Consulta del proyectista
            p['proyectista'] = models.Usuario.objects.get(pk = p['proypropietario']).userfullname

            if 'user' in locals() and str(user.rolid) == '628acd70-f86f-4449-af06-ab36144d9d6a':

                p['dimensiones_territoriales'] = []
                dimensionesTerritoriales = list(models.DelimitacionGeografica.objects.filter(proyid__exact = p['proyid']).values())

                for dim in dimensionesTerritoriales:
                    tareas = list(models.Tarea.objects.filter(dimensionid__exact=dim['dimensionid'])\
                                                      .filter(proyid = p['proyid'])\
                                                      .values())

                    dim['tareas'] = tareas

                    p['dimensiones_territoriales'].append(dim)

            listadoProyectos.append(p)

        if all is not None and all == "1":

            data = {
                'code': 200,
                'proyectos': listadoProyectos,
                'status': 'success'
            }

        else:

            # Paginación
            paginator = Paginator(listadoProyectos, 10)

            # Validación de página
            if page is None:
                page = 1

            #Petición de página
            proyectos = paginator.page(page).object_list

            data = {
                'code': 200,
                'paginator': {
                    'currentPage': int(page),
                    'perPage': paginator.per_page,
                    'lastPage': paginator.num_pages,
                    'total': paginator.count
                },
                'proyectos': proyectos,
                'status': 'success',
            }

    except EmptyPage:

        data = {
            'code': 404,
            'message': 'Página inexistente',
            'status': 'error'
        }

    except IndexError:
        data = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:
        data = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoProyecto(request):

    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'], settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

    proyNombre = request.POST.get('proynombre')
    proyDescripcion = request.POST.get('proydescripcion')
    tipoProyecto = request.POST.get('tiproid')
    proyIdExterno = 12345
    proyFechaCreacion = datetime.today()
    proyfechainicio = request.POST.get('proyfechainicio')
    proyFechaCierre = request.POST.get('proyfechacierre')
    proyEstado = 1
    decisiones = json.loads(request.POST.get('decisiones'))
    contextos = json.loads(request.POST.get('contextos'))
    equipos = json.loads(request.POST.get('plantillas'))
    propietario = tokenDecoded['user_id']
    delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')

    proyecto = models.Proyecto(proynombre = proyNombre, proydescripcion = proyDescripcion, proyidexterno = proyIdExterno, \
                               proyfechacreacion = proyFechaCreacion, proyfechainicio = proyfechainicio, proyfechacierre = proyFechaCierre, \
                               proyestado = proyEstado, proypropietario = propietario, tiproid=tipoProyecto)

    try:
        proyecto.full_clean()

        if delimitacionGeograficas is None:
            raise ValidationError({'delitacionesGeograficas': 'Requerido'})

        proyecto.save()

        almacenarDecisionProyecto(proyecto, decisiones)
        almacenarContextosProyecto(proyecto, contextos)
        almacenarDelimitacionesGeograficas(proyecto, delimitacionGeograficas)
        asignarEquipos(proyecto, equipos)

        data = serializers.serialize('python', [proyecto])[0]

        data = {
            'code': 201,
            'proyecto': data,
            'status': 'success'
        }

    except ValidationError as e:

        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        data = {
            'code': 400,
            'errors': errors,
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'message': str(e),
            'status': 'success'
        }

    except ObjectDoesNotExist as e:
        data = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

def almacenarDecisionProyecto(proyecto, decisiones):

    try:
        for decision in decisiones:

            decisionProyecto = None

            decisionProyecto = models.DecisionProyecto(proyid = proyecto.proyid, desiid = decision)

            decisionProyecto.save()

        return True

    except ValidationError as e:
        return False

def almacenarContextosProyecto(proyecto, contextos):

    try:
        for contexto in contextos:

            contextoProyecto = models.ContextoProyecto(proyid = proyecto.proyid, contextoid = contexto)

            contextoProyecto.save()

            del contextoProyecto

        return True

    except ValidationError as e:
        return False

def almacenarDelimitacionesGeograficas(proyecto, delimitacionesGeograficas):

    try:

        delimitaciones = json.loads(delimitacionesGeograficas)

        with transaction.atomic():

            for d in delimitaciones:
                delimitacion = models.DelimitacionGeografica(proyid = proyecto.proyid, nombre = d['nombre'], geojson = d['geojson'])

                delimitacion.full_clean()

                delimitacion.save()

                del delimitacion

        data = {
            'result': True
        }

    except ValidationError as e:

        data = {
            'result': False,
            'message': dict(e)
        }

    return data

def asignarEquipos(proyecto, equipos):

    with transaction.atomic():

        for equipo in equipos:

            plantilla = models.PlantillaEquipo.objects.get(pk=equipo)

            usuarios = models.MiembroPlantilla.objects.filter(planid__exact=equipo)

            for usuario in usuarios:

                integrante = models.Equipo(userid=usuario.userid, proyid=proyecto.proyid)
                integrante.save()

@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarProyecto(request, proyid):

    try:
        proyecto = models.Proyecto.objects.get(pk = proyid)

        proyecto.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarProyecto(request, proyid):
    try:
        proyecto = models.Proyecto.objects.get(pk=proyid)

        proyecto.proynombre = request.POST.get('proynombre')
        proyecto.proydescripcion = request.POST.get('proydescripcion')
        proyecto.tiproid = request.POST.get('tiproid')
        proyecto.proyfechainicio = request.POST.get('proyfechainicio')
        proyecto.proyfechacierre = request.POST.get('proyfechacierre')

        proyecto.full_clean()
        proyecto.save()

        if(request.POST.get('decisiones') is not None  and request.POST.get('contextos') is not None):

            decisiones = json.loads(request.POST.get('decisiones'))
            contextos = json.loads(request.POST.get('contextos'))

            # ================ Actualizacion de decisiones ===============================

            if len(decisiones) > 0:

                #Eliminando decisiones actuales
                decisionesProyecto = models.DecisionProyecto.objects.filter(proyid__exact=proyecto.proyid)

                if decisionesProyecto.exists():

                    for decisionProyecto in decisionesProyecto:
                        decisionProyecto.delete()

                # Añadiendo las nuevas decisiones
                for decision in decisiones:

                    decisionProyecto = models.DecisionProyecto(proyid = proyecto.proyid, desiid = decision)
                    decisionProyecto.save()

            # ============== Actualización de contextos ================================

            if len(contextos) > 0:

                # Eliminando contextos actuales
                contextosProyecto = models.ContextoProyecto.objects.filter(proyid__exact=proyecto.proyid)

                if contextosProyecto.exists():

                    for contextoProyecto in contextosProyecto:
                        contextoProyecto.delete()

                # Añadiendo las nuevos contextos
                for contexto in contextos:

                    contextoProyecto = models.ContextoProyecto(proyid = proyecto.proyid, contextoid = contexto)
                    contextoProyecto.save()

        return JsonResponse(serializers.serialize('python', [proyecto]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:

        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

@api_view(['GET'])
@permission_classes((AllowAny,))
def detalleProyecto(request, proyid):

    try:
        query = "select p.proynombre, p.proydescripcion, p.proyfechacreacion, p.proyfechainicio, p.proyfechacierre, p.proyestado, u.userfullname as proyectista  from v1.proyectos as p inner join v1.usuarios as u on u.userid = p.proypropietario where p.proyid = '" + proyid + "'"
        with connection.cursor() as cursor:

            cursor.execute(query)

            proyecto = dictfetchall(cursor)

            if(len(proyecto) > 0):

                # Obtención de Tareas
                #tareas = models.Tarea.objects.filter(proyid__exact = proyid).values()
                queryTasks = "select t.*, i.instrnombre, p.proynombre from v1.tareas as t inner join v1.proyectos as p on t.proyid = p.proyid inner join v1.instrumentos as i on t.instrid = i.instrid where t.proyid = '" + proyid + "'"
                cursor.execute(queryTasks)
                tareas = dictfetchall(cursor)

                for t in tareas:
                    if(t['taretipo'] == 1):

                        encuestas = models.Encuesta.objects.filter(tareid__exact=t['tareid'])
                        progreso = (len(encuestas) * 100) / t['tarerestriccant']
                        t['progreso'] = progreso

                        # instrumento = models.Instrumento.objects.get(pk = t['instrid'])
                        # detalleFormulario = detalleFormularioKoboToolbox(instrumento.instridexterno)
                        #
                        # if detalleFormulario:
                        #     t['progreso'] = (detalleFormulario['deployment__submission_count'] * 100) / t['tarerestriccant']

                data = {
                    'code': 200,
                    'detail':{
                      'proyecto': proyecto[0],
                      'tareas': list(tareas)
                    },
                    'status': 'success'
                }

            else:
                raise ObjectDoesNotExist

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': "error",
        }

    except DataError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'], safe = False)

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def dimensionesTerritoriales(request, proyid):

    try:
        models.Proyecto.objects.get(pk = proyid)

        dimensionesTerritoriales = models.DelimitacionGeografica.objects.filter(proyid__exact = proyid).values()

        data = {
            'code': 200,
            'dimensionesTerritoriales': list(dimensionesTerritoriales),
            'status': 'success'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'status': 'error'
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

def listadoProyectosView(request):

    return render(request, 'proyectos/listado.html')

def gestionProyectosView(request):

    return render(request, "proyectos/gestion-proyectos-mapa.html")

def tareasProyectoView(request, proyid):

    try:
        proyecto = models.Proyecto.objects.get(pk=proyid)
        data =  render(request, 'tareas/listado.html', {'proyecto':proyecto})
    except ObjectDoesNotExist:
        data = HttpResponse("", status=404)
    except ValidationError:
        data = HttpResponse("", status=400)

    return data

