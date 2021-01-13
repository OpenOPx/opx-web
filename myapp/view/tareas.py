from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import(
    Paginator,
    EmptyPage
)
from django.db import (connection, transaction)
from django.forms.models import model_to_dict
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp.view import koboclient, notificaciones
from myapp.view.utilidades import dictfetchall, obtenerParametroSistema, getPersonsIdByProject, usuarioAutenticado
from myapp.view.notificaciones import gestionCambios

ROL_SUPER_ADMIN = '8945979e-8ca5-481e-92a2-219dd42ae9fc'
ROL_PROYECTISTA = '628acd70-f86f-4449-af06-ab36144d9d6a'
ROL_VOLUNTARIO = '0be58d4e-6735-481a-8740-739a73c3be86'
ROL_VALIDADOR = '53ad3141-56bb-4ee2-adcf-5664ba03ad65'


# =========================== Tareas ==============================

##
# @brief recurso de almacenamiento de Tareas
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoTarea(request):
    restricciones = models.TaskRestriction(
        start_time = request.POST.get('HoraInicio'),
        end_time = request.POST.get('HoraCierre'),
        task_start_date = request.POST.get('tarfechainicio'),
        task_end_date = request.POST.get('tarfechacierre')
    )

    territorioSubconjunto = models.TerritorialDimension(
        dimension_name = request.POST.get('nombreSubconjunto'),
        dimension_geojson = request.POST.get('geojsonsubconjunto'),
        dimension_type = models.DimensionType.objects.get(pk = "35b0b478-9675-45fe-8da5-02ea9ef88f1b")
    )

    territorioSubconjunto.full_clean()
    territorioSubconjunto.save()

    restricciones.full_clean()
    restricciones.save()
    proyid = request.POST.get('proyid')

    dimen = models.TerritorialDimension.objects.get(pk = request.POST.get('dimensionIDparaTerritorialD'))

    with transaction.atomic():
        tarea = models.Task(
            task_name = request.POST.get('tarenombre'),
            task_type = models.TaskType.objects.get(pk = request.POST.get('taretipo')),
            task_quantity = request.POST.get('tarerestriccant'),
            task_priority = models.TaskPriority.objects.get(priority_number = request.POST.get('tareprioridad')),
            task_description = request.POST.get('taredescripcion'),
            project = models.Project.objects.get(pk = proyid),
            task_observation = "esto es para reportes",
            proj_dimension = dimen,
            instrument = models.Instrument.objects.get(pk = request.POST.get('instrid')),
            territorial_dimension = territorioSubconjunto,
            task_restriction = restricciones,
        )

        try:
            tarea.full_clean()
            tarea.save()
            data = serializers.serialize('python', [tarea])

            response = {
                'code':     201,
                'tarea':    data,
                'status':   'success'
            }

        except ValidationError as e:
            territorioSubconjunto.delete()
            restricciones.delete()
            response = {
                'code':     400,
                'errors':   dict(e),
                'status':   'error'
            }

        except IntegrityError as e:
            territorioSubconjunto.delete()
            restricciones.delete()
            response = {
                'code':     400,
                'message':  str(e),
                'status':   'success'
            }

    return JsonResponse(response, safe=False, status=response['code'])##

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoCampana(request):
    restricciones = models.TaskRestriction(
        start_time = request.POST.get('HoraInicio'),
        end_time = request.POST.get('HoraCierre'),
        task_start_date = request.POST.get('tarfechainicio'),
        task_end_date = request.POST.get('tarfechacierre')
    )

    territorioSubconjunto = models.TerritorialDimension(
        dimension_name = request.POST.get('nombreSubconjunto'),
        dimension_geojson = request.POST.get('geojsonsubconjunto'),
        dimension_type = models.DimensionType.objects.get(pk = "35b0b478-9675-45fe-8da5-02ea9ef88f1b")
    )

    territorioSubconjunto.full_clean()
    territorioSubconjunto.save()

    restricciones.full_clean()
    restricciones.save()
    proyid = request.POST.get('project_id')

    dimen = models.TerritorialDimension.objects.get(pk = request.POST.get('dimensionIDparaTerritorialD'))

    with transaction.atomic():
        tarea = models.Task(
            task_name = request.POST.get('task_name'),
            task_type = models.TaskType.objects.get(pk = request.POST.get('task_type_id')),
            task_quantity = request.POST.get('task_quantity'),
            task_priority = models.TaskPriority.objects.get(priority_id = request.POST.get('task_priority_id')),
            task_description = request.POST.get('task_description'),
            project = models.Project.objects.get(pk = proyid),
            task_observation = "esto es para reportes",
            proj_dimension = dimen,
            instrument = models.Instrument.objects.get(pk = request.POST.get('instrument_id')),
            territorial_dimension = territorioSubconjunto,
            task_restriction = restricciones,
        )

        try:
            tarea.full_clean()
            tarea.save()
            data = serializers.serialize('python', [tarea])

            response = {
                'code':     201,
                'tarea':    data,
                'status':   'success'
            }

        except ValidationError as e:
            territorioSubconjunto.delete()
            restricciones.delete()
            response = {
                'code':     400,
                'errors':   dict(e),
                'status':   'error'
            }

        except IntegrityError as e:
            territorioSubconjunto.delete()
            restricciones.delete()
            response = {
                'code':     400,
                'message':  str(e),
                'status':   'success'
            }

    return JsonResponse(response, safe=False, status=response['code'])##

##
# @brief recurso que provee el listado de tareas
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoTareas(request):

    try:
        # Obtener usuario autenticado
        usuario = usuarioAutenticado(request)
        person = models.Person.objects.get(user__userid = usuario.userid)
        tareasUsuario = []
        proyectosUsuario = []
        n = ""
        # Superadministrador
        if str(person.role_id) == ROL_SUPER_ADMIN:
            tareasUsuario = []
            n="select tk.* from opx.task as tk order by tk.task_creation_date DESC;"

        # Consulta de proyectos para un usuario proyectista
        elif str(person.role_id) == ROL_PROYECTISTA:
            n="select tk.*, restric.* \
                from opx.person as persona  \
                inner join opx.project as proyecto on proyecto.proj_owner_id = persona.pers_id  \
                inner join opx.task as tk on tk.project_id = proyecto.proj_id \
                inner join opx.task_restriction as restric on tk.task_restriction_id = restric.restriction_id  \
                where persona.pers_id = '"+str(person.pers_id)+"' order by tk.task_creation_date DESC;"

        # Consulta de proyectos para un usuario voluntario o validador
        elif str(person.role_id) == ROL_VOLUNTARIO or str(person.pers_id) == ROL_VALIDADOR:
            n="select distinct tk.*, restric.* \
                from opx.person as person \
                inner join opx.team_person as tp on person.pers_id = tp.person_id \
                inner join opx.project_team as pt on tp.team_id = pt.team_id \
                inner join opx.task as tk on tk.project_id = pt.project_id \
                inner join opx.task_restriction as restric on tk.task_restriction_id = restric.restriction_id \
                where person.pers_id = '"+str(person.pers_id)+"' order by tk.task_creation_date DESC;"   

      # ================ Obtener página validación de la misma ========================
        page = request.GET.get('page')

        if (page is None):
            page = 1

        all = request.GET.get('all')
       

        with connection.cursor() as cursor:
            cursor.execute(n)

            # formatear respuesta de base de datos
            tareas = dictfetchall(cursor)
       
        # Progreso de las Tareas
        for t in tareas:
            t['task_type_name'] = (models.TaskType.objects.get(pk = t['task_type_id'])).task_type_name
            t['instrument_name']= (models.Instrument.objects.get(pk = t['instrument_id'])).instrument_name
            t['proj_name']= (models.Project.objects.get(pk = t['project_id'])).proj_name
            t['priority_name']= (models.TaskPriority.objects.get(pk = t['task_priority_id'])).priority_name

            # Tipo encuesta
            if t['task_type_id'] == 1:
                encuestas = models.Survery.objects.filter(task_id__exact=t['task_id']) #Me quedé varado en el survey
                if t['task_completness'] != 0:
                    progreso = (len(encuestas) * 100) / t['task_completness']
                    t['task_quantity'] = progreso

        # Obtener Búsqueda y validación de la misma
        search = request.GET.get('search')
        
        if search is not  None:
            tareas = models.Task.objects.filter(task_name__icontains = search)
            tareas = list(tareas.values())
        if all is not None and all == "1":
            data = {
                'code': 200,
                'tareas': tareas,
                'status': 'success'
            }
        else:
            # Obtener Página
            paginator = Paginator(tareas, 10)
            # Obtener lista de tareas
            tareas = paginator.page(page).object_list
            data = {
                'code': 200,
                'paginator': {
                    'currentPage': page,
                    'perPage': paginator.per_page,
                    'lastPage': paginator.num_pages,
                    'total': paginator.count
                },
                'tareas': tareas,
                'status': 'success'
            }        # Obtener Búsqueda y validación de la misma


    except EmptyPage:

        data = {
            'code': 400,
            'message': 'Página inexistente',
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])


##
# @brief recurso que provee las tareas asociadas a las dimensiónes geograficas del sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoTareasMapa(request):

    areasMedicion = []

    #Consultando dimensiones territoriales de proyectos
    dimensionesTerritoriales = models.DelimitacionGeografica.objects.all()

    for dimension in dimensionesTerritoriales:

        tareas = models.Tarea.objects.filter(dimensionid__exact = dimension.dimensionid).values();

        data = {
            'areaMedicion': model_to_dict(dimension),
            'tareas': list(tareas)
        }

        areasMedicion.append(data)

    instrumentos = models.Instrumento.objects.filter(instrtipo__exact = 2)

    for instrumento in instrumentos:

        tareas = models.Tarea.objects.filter(instrid__exact = instrumento.instrid).values()

        areaMedicion = model_to_dict(instrumento)
        areaMedicion['nombre'] = areaMedicion['instrnombre']
        del areaMedicion['instrnombre']

        data = {
            'areaMedicion': areaMedicion,
            'tareas': list(tareas)
        }

        areasMedicion.append(data)

    data = {
        'code': 200,
        'areasMedicion': areasMedicion,
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief recurso que provee el detalle de una tarea
# @param request Instancia HttpRequest
# @param tareid Identificación de una tarea
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def detalleTarea(request, tareid):

    try:
        tarea = models.Task.objects.get(pk = tareid)
        restricciones = models.TaskRestriction.objects.get(pk = tarea.task_restriction.restriction_id)
        tareaDict = model_to_dict(tarea)
        restriccionesDict = model_to_dict(restricciones)
        
        # Tipo encuesta
        if tareaDict['task_type'] == 1:

            encuestas = models.Survery.objects.filter(task_id__exact=tarea.task_id)
            progreso = (len(encuestas) * 100) / tareaDict['task_quantity']
            tareaDict['task_completness'] = progreso
            tareaDict['task_start_date'] = restricciones.task_start_date
            tareaDict['task_end_date'] = restricciones.task_end_date
            tareaDict['start_time'] = restricciones.start_time
            tareaDict['end_time'] = restricciones.end_time
            # instrumento = models.Instrumento.objects.get(pk=tareaDict['instrid'])
            # detalleFormulario = detalleFormularioKoboToolbox(instrumento.instridexterno)
            #
            # if detalleFormulario:
            #     progreso = (detalleFormulario['deployment__submission_count'] * 100) / tareaDict['tarerestriccant']
            #     tareaDict['progreso'] = progreso

        data = {
            'code': 200,
            'status': 'success',
            'tarea': tareaDict,
            'restriccion': restriccionesDict
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'], safe = False)

# # @brief recurso de eliminación de tareas
# @param request Instancia HttpRequest
# @param tareid Identificación de una tarea
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarTarea(request, tareid):

    try:
        tarea = models.Task.objects.get(pk = tareid)
        restriccion = models.TaskRestriction.objects.get(pk = tarea.task_restriction.restriction_id)

        subterritorio = models.TerritorialDimension.objects.get(pk = tarea.territorial_dimension.dimension_id)

        
        tarea.delete()
        restriccion.delete()
        subterritorio.delete()



        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief recurso de actualización de tareas
# @param request Instancia HttpRequest
# @param tareid Identificación de una tarea
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarTarea(request, tareid):
    try:

        with transaction.atomic():

            estado = 0
            tarea = models.Task.objects.get(pk=tareid)


            restriction = models.TaskRestriction.objects.get(pk = request.POST.get('task_restriction_id'))
            restriction.start_time = request.POST.get('tarfechainicio')
            restriction.task_end_date = request.POST.get('tarfechacierre')
            restriction.start_time = request.POST.get('HoraInicio')
            restriction.end_time = request.POST.get('HoraCierre')
            restriction.save()

            taskpriority = models.TaskPriority.objects.get(pk = request.POST.get('task_priority_id'))

            tasktipe = models.TaskType.objects.get(pk = request.POST.get('task_type_id'))
        

            projecto = models.Project.objects.get(pk = request.POST.get('project_id'))
            tarea.task_name = request.POST.get('task_name')
            tarea.task_type = tasktipe
            tarea.task_quantity = request.POST.get('task_quantity')
            tarea.project = projecto
            tarea.task_description = request.POST.get('task_description')
            tarea.task_priority = taskpriority
            tarea.task_restriction = restriction
            tarea.save()

            """
            if estado == 2 and tarea.tareestado != 2:

                if validarTarea(tarea):

                    tarea.tareestado = estado
                    tarea.save()

            else:

                tarea.tareestado = estado
                tarea.save()

            # Verificando que el recurso haya sido llamado desde Gestión de Cambios
            if request.POST.get('gestionCambio', None) is not None:

                # Obtener los usuarios que hacen del proyecto
                usuarios = obtenerEmailsEquipo(tarea.proyid)

                # Detalle del Cambio
                detalle = "Encuestas Objetivo: {}".format(tarea.tarerestriccant)

                # Enviar Notificaciones
                gestionCambios(usuarios, 'tarea', tarea.task_name, 1, detalle)"""

            response = {
                'code': 200,
                'tarea': serializers.serialize('python', [tarea])[0],
                'status': 'success'
            }

    except ObjectDoesNotExist as e:
        response = {
            'code': 404,
            'message': str(e),
            'status': 'error' + str(e)
        }

    except ValidationError as e:

        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        response = {
            'code': 400,
            'errors': errors,
            'status': 'error'
        }

    except IntegrityError as e:
        response = {
            'code': 500,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarTareaGestionCambios(request, tareid):
    try:

        with transaction.atomic():

            estado = 0
            tarea = models.Task.objects.get(pk=tareid)

            restriction = models.TaskRestriction.objects.get(pk = request.POST.get('task_restriction_id'))
            restriction.task_start_date = request.POST.get('task_start_date')
            restriction.task_end_date = request.POST.get('task_end_date')
            restriction.start_time = request.POST.get('start_time')
            restriction.end_time = request.POST.get('end_time')
            restriction.save()

            tarea.task_quantity = request.POST.get('task_quantity')
            tarea.save()

            # Obtener los usuarios que hacen del proyecto
            pers_ids = getPersonsIdByProject(tarea.project.proj_id)
            change = {
                'start_date': request.POST.get('task_start_date'),
                'end_date': request.POST.get('task_end_date'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'task_quantity': request.POST.get('task_quantity')
            }
            notificaciones.notify(pers_ids, notificaciones.CAMBIO_FECHA_TAREA, None, change, project_name=tarea.project.proj_name, task_name=tarea.task_name)

            response = {
                'code': 200,
                'tarea': serializers.serialize('python', [tarea])[0],
                'status': 'success'
            }

    except ObjectDoesNotExist as e:
        response = {
            'code': 404,
            'message': str(e),
            'status': 'error' + str(e)
        }

    except ValidationError as e:

        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        response = {
            'code': 400,
            'errors': errors,
            'status': 'error'
        }

    except IntegrityError as e:
        response = {
            'code': 500,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])


##
# @brief Función que se encarga de validar una tarea especifica
# @param tarea Instancia del modelo Tarea
# @return Booleano
#
def validarTarea(tarea):

    if ((tarea.tareestado == 1 and tarea.task_type_id == 1) or (tarea.tareestado != 2 and tarea.taretipo == 2)):

        if tarea.task_type_id == 1:

            encuestasSinValidar = models.Encuesta.objects.filter(instrid__exact=tarea.instrid) \
                                                         .filter(estado__exact=0)

            if len(encuestasSinValidar) == 0:

                aportePositivo = int(obtenerParametroSistema('aporte-positivo-encuesta'))
                aporteNegativo = int(obtenerParametroSistema('aporte-negativo-encuesta'))

                encuestas = models.Encuesta.objects.filter(instrid__exact=tarea.instrid)

                with transaction.atomic():
                    for encuesta in encuestas:

                        if encuesta.estado == 1:
                            puntaje = aporteNegativo

                        elif encuesta.estado == 2:
                            puntaje = aportePositivo

                        asignacionPuntaje(encuesta.userid, tarea.tareid, puntaje)

                response = True

            else:
                raise ValidationError(['Todas las encuestas deben ser validadas'])

        elif tarea.task_type_id == 2:

            cartografias = models.Cartografia.objects.filter(instrid__exact=tarea.instrid)

            if len(cartografias) > 0:

                aportePositivo = int(obtenerParametroSistema('aporte-positivo-cartografia'))
                aporteNegativo = int(obtenerParametroSistema('aporte-negativo-cartografia'))

                with transaction.atomic():

                    for cartografia in cartografias:

                        # Si las cartografias no fueron marcadas como malas se marcan como buenas
                        if cartografia.estado == 0:
                            cartografia.estado = 2
                            cartografia.save()
                            puntaje = aportePositivo

                        if cartografia.estado == 1:
                            puntaje = aporteNegativo

                        if cartografia.estado == 2:
                            puntaje = aportePositivo

                        asignacionPuntaje(cartografia.userid, tarea.tareid, puntaje)

                response = True

            else:
                raise ValidationError(['No hay cartografias'])
    else:
        raise ValidationError(['La tarea no esta terminada o ya fue validada'])

    return response

##
# @brief Funcion que se encarga de aumentar el puntaje actual de un usuario
# @param userid Identificación del usuario
# @param tareid Identificación de una tarea
# @param puntaje puntaje a sumar o restar para un usuario
#
def asignacionPuntaje(userid, tareid, puntaje):

    # Almacenar historial de asignación
    asignacion = models.AsignacionPuntaje(userid=userid, tareid=tareid, puntaje=puntaje)
    asignacion.save()

    #Asignacion de puntos correspondientes
    usuario = models.Usuario.objects.get(pk=userid)
    usuario.puntaje = usuario.puntaje + puntaje
    usuario.save()

    promoverUsuario(usuario)

##
# @brief Función que promueve un usuario de rol en caso tal cumpla con el puntaje requerido
# @param user Instancia del modelo Usuario
#
def promoverUsuario(user):

    puntajeValidador = int(obtenerParametroSistema('umbral-validador'))
    puntajeProyectista = obtenerParametroSistema('umbral-proyectista')

    # Promoción de voluntario a validador
    if user.rolid == ROL_VOLUNTARIO and user.puntaje >= puntajeValidador:
        user.rolid = ROL_VALIDADOR
        user.save()

        notificacionPromocionUsuario(user, 'Validador')

    # Promocion de Validador a Proyectista
    if user.rolid == ROL_VALIDADOR and user.puntaje >= puntajeProyectista:
        user.rolid = ROL_PROYECTISTA
        user.save()

        notificacionPromocionUsuario(user, 'Proyectista')

##
# @brief Función que envía una notificación via correo a un usuario cuando es promovido de Rol
# @param user Instancia del modelo Usuario
# @param rol Nombre del nuevo rol del usuario
#
def notificacionPromocionUsuario(user, rol):

    subject = "Notificación OPC"
    message = "<p>Felicitaciones. Ahora eres " + rol

    # Envío de correo electrónico
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.useremail],
        fail_silently=False,
        html_message=message
    )

##
# @brief Recurso que provee las tareas que hacen parte de una dimensión geográfica
# @param request Instancia HttpRequest
# @param dimensionid Identificación de la dimensión geográfica
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def tareasXDimensionTerritorial(request, proj_id):

    try:
        #dimensionTerritorial = models.TerritorialDimension.objects.get(pk=dimensionid) nunca lo usaron

        tareas = models.Task.objects.filter(project__proj_id__exact=proj_id).values()

        response = {
            'code': 200,
            'data': list(tareas),
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
# @brief Función que provee la plantilla HTML para la gestión de tareas
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoTareasView(request):

    return render(request, 'tareas/listado.html')