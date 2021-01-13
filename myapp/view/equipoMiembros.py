
from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from django.forms.models import model_to_dict

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
from myapp.view.utilidades import usuarioAutenticado, dictfetchall

##
# @brief Recurso de listado de integrantes de una plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de plantilla de equipo
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoMiembros(request, planid):

    try:
        #miembrosPlantilla = MiembroPlantilla.objects.filter(planid__exact=planid).values()
        with connection.cursor() as cursor:
            query = "select mp.teampers_id, u.*, nei.neighb_name \
                    from opx.team_person as mp \
                    inner join opx.person as u on u.pers_id = mp.person_id  \
                    inner join opx.neighborhood as nei on nei.neighb_id = u.neighborhood_id \
                    where mp.team_id = '"+planid+"' order by u.pers_score DESC"

            cursor.execute(query)

            miembrosPlantilla = dictfetchall(cursor)
        
            response = {
                'code': 200,
                'data': miembrosPlantilla,
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
# @brief Recurso de Inserción de usuario a una plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de plantilla de equipo
# @return cadena JSON
#

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def agregarMiembro(request, planid):

    try:
        with transaction.atomic():
            personaId = request.POST.get('usuarioId')

            persona = models.Person.objects.get(user__userid = personaId)

            equipo = models.Team.objects.get(pk=planid)

            equipoPersona = models.TeamPerson.objects.filter(person__pers_id__exact = persona.pers_id).filter(team__team_id__exact = equipo.team_id)

            if len(equipoPersona) == 0:
                equipoMiembro = models.TeamPerson(
                person = persona,
                team = equipo
                )
                equipoMiembro.full_clean()
                equipoMiembro.save()
                #notificación del cambio a la persona
                change={
                    'team_name' : equipo.team_name
                }
                notificaciones.notify([persona.pers_id], notificaciones.CAMBIO_EQUIPO, notificaciones.AGREGADO_A_EQUIPO, change)
                response = {
                    'code': 201,
                    'data': model_to_dict(equipoMiembro),
                    'status': 'success'
                }
            
            else:
                response = {
                'code': 403,
                'message': 'El usuario ya está registrado en el equipo',
                'status': 'error'
                }
        
    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
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

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que provee el listado de usuarios que se pueden agregar a una plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de plantilla de equipo
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def miembrosDisponibles(request, planid):


    try:
        equipoMiembro = models.Team.objects.get(pk = planid)

        # Busqueda de Usuarios
        search = request.GET.get('search')

        query = "select u.user_id, u.pers_name, u.pers_lastname, u.pers_score, nei.neighb_name \
                from opx.person u \
                inner join opx.neighborhood as nei on nei.neighb_id = u.neighborhood_id \
                where (u.role_id = '0be58d4e-6735-481a-8740-739a73c3be86' or u.role_id = '53ad3141-56bb-4ee2-adcf-5664ba03ad65') and u.isactive = 1 and u.pers_id not in (select mp.person_id from opx.team_person mp where mp.team_id = '"+planid+"') order by u.pers_score DESC"

        if search is not None:
            query += "and u.pers_name ~* '" + search + "'"

        with connection.cursor() as cursor:
            cursor.execute(query)

            usuarios = dictfetchall(cursor)

        response = {
            'code': 200,
            'data': usuarios,
            'status': 'success'
        }

    except ObjectDoesNotExist:

        response = {
            'code': 404,
            'message': 'La plantilla no existe',
            'status': 'error'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': list(e)[0],
            'status': 'error'
        }

    return JsonResponse(response, safe = False, status = response['code'])

    ##

# @brief Recurso de eliminación de usuario de una plantilla de equipo
# @param request Instancia HttpRequest
# @param miplid Identificación de asignación de usuario a plantilla de equipo
# @return cadena JSON
#
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def eliminarMiembro(request, miplid):

    try:
        with transaction.atomic():
            miembroPlantilla = models.TeamPerson.objects.get(pk=miplid)
            equipo = models.Team.objects.get(pk=miembroPlantilla.team.team_id)

            miembroPlantilla.delete()
            #notificación del cambio a la persona
            change={
                'team_name' : equipo.team_name
            }
            notificaciones.notify([miembroPlantilla.person.pers_id], notificaciones.CAMBIO_EQUIPO, notificaciones.ELIMINADO_DE_EQUIPO, change)
            

            response = {
                'code': 200,
                'status': 'success'
            }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': list(e)[0],
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])