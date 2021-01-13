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
from myapp.view import notificaciones
from myapp.view.utilidades import usuarioAutenticado, reporteEstadoProyecto, dictfetchall, getPersonsIdByProject

ROL_SUPER_ADMIN = '8945979e-8ca5-481e-92a2-219dd42ae9fc'
ROL_PROYECTISTA = '628acd70-f86f-4449-af06-ab36144d9d6a'
ROL_VOLUNTARIO = '0be58d4e-6735-481a-8740-739a73c3be86'
ROL_VALIDADOR = '53ad3141-56bb-4ee2-adcf-5664ba03ad65'

##
# @brief Función que provee una plantilla HTML para la gestión de proyectos
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoProyectosView(request):
    return render(request, 'proyectos/listado.html')

##
# @brief Función que provee una plantilla HTML para la gestión de cambios de un proyecto
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def gestionProyectosView(request):
    return render(request, "proyectos/gestion-proyectos-mapa.html")

    ##

# @brief Recurso de listado de proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def listadoProyectos(request):
    search = request.GET.get('search')
    page = request.GET.get('page')
    all = request.GET.get('all')

    try:
        if 'HTTP_AUTHORIZATION' in request.META.keys() and request.META['HTTP_AUTHORIZATION'] != 'null':

            # # Decodificando el access token
            # tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
            #                             settings.SIMPLE_JWT['VERIFYING_KEY'])
            # tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
            # #consultando el usuario
            # user = models.Usuario.objects.get(pk = tokenDecoded['user_id'])
            user = usuarioAutenticado(request)

            # ============================ Consultando proyectos ====================================

            #Consulta de proyectos para super administrador
            person = models.Person.objects.get(user__userid = user.userid)
                
            if str(person.role.role_id) == ROL_SUPER_ADMIN:
                proyectos = models.Project.objects.all()
                # Especificando orden
                proyectos = proyectos.order_by('-proj_creation_date')
                # convirtiendo a lista de diccionarios
                proyectos = list(proyectos.values())

            # Consulta de proyectos para proyectista
            elif str(person.role.role_id) == ROL_PROYECTISTA:
                proyectos = models.Project.objects.filter(proj_owner__pers_id__exact = person.pers_id)
                # Especificando orden
                proyectos = proyectos.order_by('-proj_creation_date')
                # convirtiendo a lista de diccionarios
                proyectos = list(proyectos.values())

            # Consulta de proyectos para voluntarios o validadores
            elif str(person.role.role_id) == ROL_VOLUNTARIO or str(person.role.role_id) == ROL_VALIDADOR:

                #consultar los proyectos a los que está asociado el voluntario o validador
                query = "select distinct pj.* from opx.team_person as tp inner join opx.project_team as pt on pt.team_id = tp.team_id inner join opx.project as pj on pt.project_id = pj.proj_id where tp.person_id = '"+str(person.pers_id)+"' order by pj.proj_creation_date DESC;"

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    PJ = dictfetchall(cursor)
                    proyectos = list(PJ)

            #Tipo de usuario distinto
            else:
                proyectos = models.Project.objects.filter(proj_name = 'qwerty')

        # Usuario Invitado
        else:
            proyectos = models.Project.objects.all()

        # ================= Busqueda de proyectos
        if search:
            proyectos = models.Project.objects.filter(proj_name__icontains = search)
            proyectos = list(proyectos.values())



        listadoProyectos = []
        type(proyectos)
        for p in proyectos:
            type(p)
            #Consulta del proyectista
            name = p['proj_external_id']
            #proj_owner_id = p['proj_owner_id']
            persona = models.Person.objects.get(pk = p['proj_owner_id'])
            p['proyectista'] = persona.pers_name + ' ' + persona.pers_lastname 

            if 'user' in locals() and (str(person.role.role_id) == ROL_PROYECTISTA or str(person.role.role_id) == ROL_SUPER_ADMIN):

                p['dimensiones_territoriales'] = []

                query = "select dim.* from opx.territorial_dimension as dim inner join opx.project_dimension as pd on pd.territorial_dimension_id = dim.dimension_id where pd.project_id = '"+ str(p['proj_id']) +"';"

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    territorios = dictfetchall(cursor)
                    p['dimensiones_territoriales'] = list(territorios)

                query1 = "select tarea.*, dim.* from opx.task as tarea \
                        inner join opx.territorial_dimension as dim on dim.dimension_id = tarea.territorial_dimension_id \
                        where tarea.project_id = '"+str(p['proj_id'])+"';"
                with connection.cursor() as cursor:
                    cursor.execute(query1)
                    tareas = dictfetchall(cursor)
                    p['tareas'] = list(tareas)

            #Reportes
            p['reportes'] = reporteEstadoProyecto(str(p['proj_id']))

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

##
# @brief Recurso de almacenamiento de proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoProyecto(request):
    user = usuarioAutenticado(request)
    person = models.Person.objects.get(user__userid = user.userid)
    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'], settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
    delimintacionBarrio = request.POST.get('dimensionesPre')
    decisiones = request.POST.get('decisiones')
    contextos = request.POST.get('contextos')
    equipos = request.POST.get('plantillas')
    delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')
    tipoP = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
    
    try:
        with transaction.atomic():
            if((delimitacionGeograficas != "[]") and (decisiones != "[]") and (contextos != "[]") and (equipos != "[]")):
                proyecto = models.Project(
                    proj_name = request.POST.get('proynombre'),
                    proj_description= request.POST.get('proydescripcion'),
                    proj_external_id = 12345,
                    proj_close_date = request.POST.get('proyfechacierre'),
                    proj_start_date = request.POST.get('proyfechainicio'),
                    proj_completness = 0,
                    project_type = tipoP,
                    proj_owner = person
                )
                proyecto.full_clean()
                proyecto.save()

                delimintacionBarrio = json.loads(delimintacionBarrio)
                almacenarDelimitacionesPrecarga(proyecto, delimintacionBarrio)

                delimitacionGeograficas = json.loads(delimitacionGeograficas)
                almacenarDelimitacionesGeograficas(proyecto, delimitacionGeograficas)

                decisiones = json.loads(decisiones)
                almacenarDecisionProyecto(proyecto, decisiones)

                contextos = json.loads(contextos)
                almacenarContextosProyecto(proyecto, contextos)

                equipos = json.loads(equipos)
                asignarEquipos(proyecto, equipos)

                data = serializers.serialize('python', [proyecto])[0]

                data = {
                    'code': 201,
                    'proyecto': data,
                    'status': 'success'
                }
            else:
                raise ValidationError({'Información incompleta'})

    except ValidationError as e:
        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        data = {
            'code': 400,
            'errors': errors,
            'message': str(e),
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

##
# @brief Funcion que asigna decision(es) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param decisiones listado de identificadores de decisiones
# @return booleano
#
def almacenarDecisionProyecto(proyecto, decisiones):
    try:
        for decisionI in decisiones:
            desicionP = None
            decisionProyecto = None

            desicionP = models.Decision.objects.get(decs_id__exact = decisionI)

            decisionProyecto = models.ProjectDecision(
                project = proyecto, 
                decision = desicionP
            )

            decisionProyecto.save()

        return True

    except ValidationError as e:
        return False


        ##
# @brief Funcion que asigna contexto(s) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param contextos listado de identificadores de contextos
# @return booleano
#
def almacenarContextosProyecto(proyecto, contextos):

    try:
        for contexto in contextos:
            contextoP = None
            contextoProyecto = None

            contextoP = models.Context.objects.get(context_id__exact = contexto)
            contextoProyecto = models.ProjectContext(
                project = proyecto, 
                context = contextoP
            )

            contextoProyecto.save()


        return True

    except ValidationError as e:
        return False

##
# @brief Funcion que almacena las dimensiones geograficas de un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param delimitacionesGeograficas delimitaciones geograficas generadas por el mapa
# @return Diccionario
# 
def almacenarDelimitacionesGeograficas(proyecto, delimitacionesGeograficas):
    try:

            for d in delimitacionesGeograficas:
                delimitacion = None
                delimitacion = models.TerritorialDimension(
                    dimension_name = d['nombre'], 
                    dimension_geojson = d['geojson'],
                    dimension_type = models.DimensionType.objects.get(dim_type_id__exact = '35b0b478-9675-45fe-8da5-02ea9ef88f1b')
                )
                delimitacion.save()
                delimitacionP = models.ProjectTerritorialDimension(
                    project = proyecto,
                    territorial_dimension = delimitacion
                )
                delimitacionP.save()
                delimitacionP = None
        
            return True

    except ValidationError as e:
        return False

##
# @brief 
# @param proyecto instancia del modelo proyecto
# @param delimitacionesGeograficas delimitaciones geograficas generadas por el mapa
# @return Diccionario
# 
def almacenarDelimitacionesPrecarga(proyecto, delimintacionBarrio):
    try:

            for d in delimintacionBarrio:
                delimitacionP = models.ProjectTerritorialDimension(
                    project = proyecto,
                    territorial_dimension = models.TerritorialDimension.objects.get(dimension_id__exact = d)
                )
                delimitacionP.save()
                delimitacionP = None
        
            return True

    except ValidationError as e:
        return False

##
# @brief Funcion que asigna integrantes a un proyecto en base a los integrantes de una plantilla de equipo
# @param proyecto instancia del modelo proyecto
# @param equipos lista de identificadores de plantillas de equipo
#
def asignarEquipos(proyecto, equipos):
    try:
            for equipo in equipos:
                equipoP = None
                proyectoEquipo = None

                equipoP = models.Team.objects.get(pk=equipo)

                proyectoEquipo = models.ProjectTeam(
                    team = equipoP,
                    project = proyecto
                )
                proyectoEquipo.save()
    
            return True

    except ValidationError as e:
        return False

##
# @brief recurso de actualización de proyectos
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarProyecto(request, proyid):
    try:
        proyecto = models.Project.objects.get(pk=proyid)
        delimintacionBarrio = request.POST.get('dimensionesPre')
        decisiones = request.POST.get('decisiones')
        contextos = request.POST.get('contextos')
        equipos = request.POST.get('plantillas')
        delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')

        if((delimitacionGeograficas != "[]" or delimintacionBarrio != "[]") and (decisiones != "[]") and (contextos != "[]") and (equipos != "[]")):
            proyecto.proj_name = request.POST.get('proynombre')
            proyecto.proj_description = request.POST.get('proydescripcion')
            proyecto.project_type = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
            proyecto.proj_start_date = request.POST.get('proyfechainicio')
            proyecto.proj_close_date = request.POST.get('proyfechacierre')

            #Actualiza las decisiones
            decisiones = json.loads(decisiones)
            if len(decisiones)>0:
                decisionesP = models.ProjectDecision.objects.filter(project__proj_id__exact = proyecto.proj_id)
                if decisionesP.exists():
                    for decisionProj in decisionesP:
                        decisionProj.delete()

                for decision in decisiones:
                    descProj = models.ProjectDecision(project = proyecto, decision = models.Decision.objects.get(pk = decision))
                    descProj.save()

            #Actualiza los contextos
            contextos = json.loads(contextos)
            if len(contextos)>0:
                contextosP = models.ProjectContext.objects.filter(project__proj_id__exact = proyecto.proj_id)
                if contextosP.exists():
                    for contextoProj in contextosP:
                        contextoProj.delete() 
                
                for contexto in contextos:
                    contProj = models.ProjectContext(project = proyecto, context = models.Context.objects.get(pk = contexto))
                    contProj.save()

            proyecto.full_clean()
            proyecto.save()

        # ================== Notificación de Gestion de cambios ========================
#        if request.POST.get('gestionCambio', None) is not None:
    
            #obtener usuarios que hacen parte del proyecto:
#            usuarios = obtenerEmailsEquipo(proyid)

            # Detalle del Cambio
#            detalle = "<b> Fecha Inicio: </b> {} <br />" \
#                      "<b> Fecha Fin </b> {}" \
#                      .format(proyecto.proj_start_date, proyecto.proj_close_date)

            #Enviar notificaciones
#            gestionCambios(usuarios, 'proyecto', proyecto.proj_name, 2, detalle)

        return JsonResponse(serializers.serialize('python', [proyecto]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarProyectoBasic(request, proyid):
    try:
        proyecto = models.Project.objects.get(pk=proyid)

        
        proyecto.proj_name = request.POST.get('proj_name')
        proyecto.proj_description = request.POST.get('proj_description')
        #proyecto.project_type = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
        proyecto.proj_start_date = request.POST.get('proj_start_date')
        proyecto.proj_close_date = request.POST.get('proj_close_date')
        
        proyecto.full_clean()
        proyecto.save()

        change = {
            'start_date': request.POST.get('proj_start_date'),
            'end_date': request.POST.get('proj_close_date'),
        }
        persons = getPersonsIdByProject(proyid)
        notificaciones.notify(persons, notificaciones.CAMBIO_FECHA_PROYECTO, None, change, project_name=proyecto.proj_name)

        return JsonResponse(serializers.serialize('python', [proyecto]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)


##
# @brief recurso de eliminación de proyectos
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarProyecto(request, proyid):

    try:
        projDeci = models.ProjectDecision.objects.filter(project__proj_id = proyid)

        for p in projDeci:
            p.delete()

        projContx = models.ProjectContext.objects.filter(project__proj_id = proyid)

        for p in projContx:
            p.delete()

        projTeam = models.ProjectTeam.objects.filter(project__proj_id = proyid)
        for p in projTeam:
            p.delete()

        projTerr = models.ProjectTerritorialDimension.objects.filter(project__proj_id = proyid)
        for p in projTerr:
            p.delete()

        query = "select dim.* \
                from opx.territorial_dimension as dim \
                inner join opx.project_dimension as pd on dim.dimension_id = pd.territorial_dimension_id \
                where pd.project_id = '"+proyid+"' and dim.preloaded = 0;"

        with connection.cursor() as cursor:
            cursor.execute(query)
            territorios = dictfetchall(cursor)
            for p in territorios:
                models.TerritorialDimension.objects.get(pk = p['dimension_id']).delete()
            
        
        projComentario = models.Comment.objects.filter(project__proj_id = proyid)
        for p in projComentario:
            p.delete()

        projTask = models.Task.objects.filter(project__proj_id = proyid)
        for p in projTask:
            p.delete()

        #borrar las tareas antes de borrar e pj al igual que
        proyecto = models.Project.objects.get(pk = proyid)
        proyecto.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)


        ##

# @brief Plantilla para la gestión del equipo de un proyecto
# @param request instancia HttpRequest
# @param proyid Identificación de un proyecto
# @return cadena JSON
#
def equipoProyectoView(request, proyid):

    try:
        models.Project.objects.get(pk = proyid)
        return render(request, "proyectos/equipo.html")

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", status = 400)

##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def equipoProyecto(request, proyid):

    try:
        query = "select tm.team_name, tm.team_id, tm.team_effectiveness, tm.team_leader_id, pt.proj_team_id  from opx.project as pj inner join opx.project_team as pt on pj.proj_id = pt.project_id inner join opx.team as tm on pt.team_id = tm.team_id where pj.proj_id = '"+ proyid+"' order by tm.team_name ASC"
        with connection.cursor() as cursor:
            cursor.execute(query)
            equipos = dictfetchall(cursor)

            for n in equipos:
                n['name_owner'] = (models.Person.objects.get(pk = n['team_leader_id'])).pers_name
                n['team_miembros'] = len(models.TeamPerson.objects.filter(team__team_id__exact = n['team_id'])) 


            data = {
                'code': 200,
                'equipo': equipos,
                'status': 'success'
            }

    except ValidationError as e:

        data = {
            'code': 400,
            'equipo': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])


    ##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def equiposDisponiblesProyecto(request, proyid):

    try:
        query = "select * from opx.team as team2\
            except(select team1.* from opx.project_team as pt \
            inner join opx.team as team1 on pt.team_id = team1.team_id \
            where pt.project_id = '"+proyid+"')"
            
        with connection.cursor() as cursor:
            cursor.execute(query)
            equipos = dictfetchall(cursor)

            for n in equipos:
                n['name_owner'] = (models.Person.objects.get(pk = n['team_leader_id'])).pers_name

            data = {
                'code': 200,
                'equipo': equipos,
                'status': 'success'
            }

    except ValidationError as e:
        data = {
            'code': 400,
            'equipo': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def agregarEquipo(request):
    
    try:
        equipoId = request.POST.get('equipoId')
        proyectoId = request.POST.get('proyectoId')

        equipoP = models.Team.objects.get(pk=equipoId)
        proyectoP = models.Project.objects.get(pk=proyectoId)

        proyectoEquipo = models.ProjectTeam(
                team = equipoP,
                project = proyectoP
        )
        proyectoEquipo.save()
        
        # ===Notificación===
        person_ids = getPersonsIdByProject(proyectoId)
        change = {
            'team_name': equipoP.team_name,
            'proj_name': proyectoP.proj_name
        }
        notificaciones.notify(person_ids, notificaciones.CAMBIO_EQUIPO_PROYECTO, notificaciones.EQUIPO_AGREGADO, change, project_name=proyectoP.proj_name )

        data = {
            'code': 201,
            'integrante': serializers.serialize('python', [proyectoEquipo])[0],
            'status': 'success'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'errors': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarEquipo(request,equid):
        
    try:
        proyectoEquipo = models.ProjectTeam.objects.get(pk = equid)
        equipoP = models.Team.objects.get(pk=proyectoEquipo.team.team_id)
        proyectoP = models.Project.objects.get(pk=proyectoEquipo.project.proj_id)
        proyectoEquipo.delete()

        # ===Notificación===
        person_ids = getPersonsIdByProject(proyectoP.proj_id)
        change = {
            'team_name': equipoP.team_name,
            'proj_name': proyectoP.proj_name
        }
        notificaciones.notify(person_ids, notificaciones.CAMBIO_EQUIPO_PROYECTO, notificaciones.EQUIPO_ELIMINADO, change, project_name=proyectoP.proj_name )

        response = {
            'code': 200,
            'status': 'success'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': list(e)[0],
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])


##
# @brief recurso que provee las dimensiones geograficas de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def dimensionesTerritoriales(request, proyid):

    try:

        query= "select td.* from opx.territorial_dimension as td \
                inner join opx.project_dimension as pt on td.dimension_id = pt.territorial_dimension_id \
                inner join opx.project as pj on pj.proj_id = pt.project_id \
                where pj.proj_id = '"+proyid+"';"
       

        with connection.cursor() as cursor:
            cursor.execute(query)
            dimensionesTerritoriales = dictfetchall(cursor)

    
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


    ##

# @brief Función que provee una plantilla HTML para la gestión de tareas de un proyecto especifico
# @param request Instancia HttpRequest
# @param proyid Identificación de un proyecto
# @return plantilla HTML
#
def tareasProyectoView(request, proyid):

    try:
        proyecto = models.Project.objects.get(pk=proyid)
        data =  render(request, 'tareas/listado.html', {'proyecto':proyecto})
    except ObjectDoesNotExist:
        data = HttpResponse("", status=404)
    except ValidationError:
        data = HttpResponse("", status=400)

    return data

##
# @brief recurso que provee el detalle de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def detalleProyecto(request, proyid):

    try:
        query = "select tarea.*,tipoT.task_type_name, instrumento.instrument_name, proyecto.proj_name, prioridad.priority_name \
                from opx.project as proyecto \
                inner join opx.task as tarea on proyecto.proj_id = tarea.project_id \
                inner join opx.task_priority as prioridad on tarea.task_priority_id = prioridad.priority_id \
                inner join opx.task_type as tipoT on tarea.task_type_id = tipoT.task_type_id \
                inner join opx.instrument as instrumento on tarea.instrument_id = instrumento.instrument_id \
                where proyecto.proj_id = '"+proyid+"';"

        with connection.cursor() as cursor:
            cursor.execute(query)
            listaTareas = dictfetchall(cursor)

        data = {
            'code': 200,
            'detail':{
              #'proyecto': proyecto[0],
              'tareas': list(listaTareas)
            },
            'status': 'success'
        }

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

##
# @brief recurso que provee el detalle de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def detalleProyectoMovil(request, proyid):

    try:
        queryProyecto= "select proyecto.*, persona.pers_name, persona.pers_lastname from opx.project as proyecto inner join opx.person as persona on persona.pers_id = proyecto.proj_owner_id where proyecto.proj_id = '"+proyid+"'"

        queryTareas = "select tarea.task_id, tarea.task_name, tarea.task_description, tarea.task_quantity,  \
                        tarea.task_completness, tarea.task_creation_date, tarea.instrument_id, tarea.proj_dimension_id, \
                        tarea.project_id, tarea.task_priority_id, tarea.territorial_dimension_id, territorio.dimension_geojson, \
                        tarea.task_restriction_id, restric.*, tarea.task_type_id, tipoTarea.task_type_name \
                        from opx.task as tarea \
                        inner join opx.task_type as tipoTarea on tipoTarea.task_type_id = tarea.task_type_id \
                        inner join opx.territorial_dimension as territorio on territorio.dimension_id = tarea.territorial_dimension_id \
                        inner join opx.task_restriction as restric on restric.restriction_id = tarea.task_restriction_id \
                        where tarea.project_id = '"+proyid+"'"

        with connection.cursor() as cursor:
            cursor.execute(queryProyecto)
            infoPj = dictfetchall(cursor)
        infoPj[0]['dimensiones_territoriales'] = []

        query = "select dim.* from opx.territorial_dimension as dim inner join opx.project_dimension as pd on pd.territorial_dimension_id = dim.dimension_id where pd.project_id = '"+ str(infoPj[0]['proj_id']) +"';"

        with connection.cursor() as cursor:
            cursor.execute(query)
            territorios = dictfetchall(cursor)
            infoPj[0]['dimensiones_territoriales'] = list(territorios)   
            
        with connection.cursor() as cursor:
            cursor.execute(queryTareas)
            listaTareas = dictfetchall(cursor)     

        data = {
            'code': 200,
            'detail':{
              'proyecto': infoPj[0],
              'tareas': list(listaTareas)
            },
            'status': 'success'
        }

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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def cambioTerritorio(request, dimensionid):

    try:

        with transaction.atomic():
            project_dimension = models.TerritorialDimension.objects.get(pk=dimensionid)

            data = json.loads(request.body)
            proj_id = data['proj_id']

            if 'geojson' in data:
                #dimensionTerritorialNew = models.DelimitacionGeografica(proyid=dimensionTerritorialOld.proyid, nombre=dimensionTerritorialOld.nombre, geojson=data['geojson'])
                #dimensionTerritorialNew.save()
                project_dimension.dimension_geojson = data['geojson']
                project_dimension.save()
                if 'tareas' in data:
                    for tarea in data['tareas']:
                        task_dimension = models.TerritorialDimension.objects.get(pk = tarea['territorial_dimension_id'])
                        task_dimension.dimension_geojson = tarea['dimension_geojson']
                        task_dimension.save()

                    response = {
                        'code': 200,
                        'status': 'success'
                    }

                else:
                    raise ValidationError("JSON Inválido")

            else:
                raise ValidationError("JSON Inválido")

        # ===Notificación===
        project = models.Project.objects.get(pk=proj_id)
        change = {
            'proj_name': project.proj_name
        }
        personsid = getPersonsIdByProject(proj_id)
        notificaciones.notify(personsid, notificaciones.CAMBIO_DIMENSION_TERRITORIAL, None, change, project_name=project.proj_name)

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError as e:
        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])
    
##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def decisionesDelProyecto(request, proyid):

    try:
        query = "select des.* from opx.decision as des inner join opx.project_decision as pd on pd.decision_id = des.decs_id where pd.project_id = '"+proyid+"';"
        with connection.cursor() as cursor:
            cursor.execute(query)
            decisiones = dictfetchall(cursor)


            data = {
                'code': 200,
                'decisiones': decisiones,
                'status': 'success'
            }

    except ValidationError as e:

        data = {
            'code': 400,
            'decisiones': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])


##
# @brief 
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listaDimensionesPrecargadas(request):

        query = "select dim.dimension_id, dim.dimension_name \
                from opx.territorial_dimension as dim \
                where dim.preloaded = '1' and dim.dimension_type_id = '35b0b478-9675-45fe-8da5-02ea9ef88f1b'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            dimPre = dictfetchall(cursor)

        return JsonResponse(dimPre, safe = False)

##
# @brief 
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def mapaDimension(request):
    data = json.loads(request.body)

    dimensiones = []
    for dimenId in data['dimensiones_id']:
        dimension = models.TerritorialDimension.objects.get(pk=dimenId)
        dimensiones.append(dimension)
        
    data = {
        'code': 200,
        'geo': serializers.serialize('python', list(dimensiones)),
        'status': 'success'
    }
    return JsonResponse(data, safe = False, status = data['code'])
