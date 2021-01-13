
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
from django.conf import settings
from django.core.mail import send_mail
from fcm_django.models import FCMDevice
from myapp import models
from myapp.models import Notification
from myapp.view.utilidades import usuarioAutenticado

CAMBIO_DIMENSION_TERRITORIAL = 1
CAMBIO_FECHA_TAREA = 2
CAMBIO_EQUIPO = 3
CAMBIO_FECHA_PROYECTO = 4
CAMBIO_EQUIPO_PROYECTO = 5
AGREGADO_A_EQUIPO = 'MIEMBO_AGREGADO_A_EQUIPO'
ELIMINADO_DE_EQUIPO = 'MIEMBRO_ELIMINADO_DE_EQUIPO'
EQUIPO_AGREGADO = 'EQUIPO_AGREGADO_A_PROYECTO'
EQUIPO_ELIMINADO = 'EQUIPO_ELIMINADO_DE_PROYECTO'

##
# @brief Envio de notifificaciones correspondiente a la gestión de cambios de un proyecto especifico
# @param usuarios lista de correos electrónicos destinatarios de la notificación
# @param tipoReceptor define el tipo de entidad que sufrio cambios (proyecto o tarea)
# @param nombreReceptor define el nombre del proyecto/tarea que sufrio cambios
# @param tipoCambio Define el tipo de cambio que sufrio el proyecto/tarea.
# @param detalle información adicional del cambio efectuado
# @return cadena JSON
#
def gestionCambios(usuarios, tipoReceptor, nombreReceptor, tipoCambio, detalle=""):

    # Definición de tipos de cambio
    tiposCambio = {
        1:  'Cambio de Objetivo',
        2: 'Cambio de Tiempo',
        3: 'Cambio de Equipo',
        4: 'Cambio de Territorio'
    }

    # Asunto de la notificación via correo
    subject = "Notificacion de Cambio"

    # Verificacion de la existencia de tipo de cambio recibido
    cambio = tiposCambio.get(tipoCambio, None)

    if cambio is not None:
        message = "Hola. Ha habido un {} en {} {}." \
                  "<br /> {}" \
                  .format(cambio, tipoReceptor, nombreReceptor, detalle)

        # Envío de Notificación de Correo
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            usuarios,
            fail_silently=False,
            html_message=message
        )

        response = True

    else:
        response = False

    return response


def notify(personsid_list, notification_type, case, change, project_name=None, task_name=None):
    """
    Easy wrapper for sending a single notification to a person list through FCM. All members
    of the person list will have the notification stored in database unitl they 
    decide to empty their notification list.
    """
    print(">> Notificando cambios a usuarios...")
    try:

        description = {}
        push_message = ""
        """
        change = {
            'start_date': 'fechainicio',#TASK Y PROJ
            'end_date': 'fecha fin',
            'start_time': 'FECHA TAREA',
            'end_time': 'FECHA TREAS'
        }"""
        
        if notification_type == CAMBIO_EQUIPO:
            push_message = 'Cambio en el equipo "'+ change['team_name']+'"'
            if case == AGREGADO_A_EQUIPO:
                description = {
                    'type': 'agregado',
                    'message': 'Has sido agregado al equipo "'+ change['team_name']+'"'
                }
            if case == ELIMINADO_DE_EQUIPO:
                description = {
                    'type': 'eliminado',
                    'message': 'Has sido eliminado del equipo "'+ change['team_name']+'"'
                }
        if notification_type == CAMBIO_EQUIPO_PROYECTO:
            push_message = 'Participación en el proyecto "'+change['proj_name']+'" modificada.'
            if case == EQUIPO_AGREGADO:
                description = {
                    'type': 'Equipo agregado',
                    'message': 'El equipo "'+ change['team_name'] +'", al que perteneces, ha sido agregado al proyecto "'+change['proj_name']+'"'
                }
            if case == EQUIPO_ELIMINADO:
                description = {
                    'type': 'Equipo eliminado',
                    'message': 'El equipo "'+ change['team_name'] +'", al que perteneces, ha sido eliminado del proyecto "'+change['proj_name']+'"'
                }
        if notification_type == CAMBIO_FECHA_PROYECTO:
            push_message = 'Cambio de fecha del proyecto "'+project_name+'"'
            description = {
                'type': 'proyecto',
                'body': change
            }
        if notification_type == CAMBIO_FECHA_TAREA:
            push_message = 'Cambio en las condiciones de campaña para tarea "'+task_name+'"'
            description = {
                'type': 'tarea',
                'body': change
            }
        if notification_type == CAMBIO_DIMENSION_TERRITORIAL:
            push_message = 'Cambio de territorio del proyecto "'+change['proj_name']+'"'
            description = {
                'type': 'territorio',
                'message': 'Se cambió la dimensión territorial del proyecto "'+change['proj_name']+'"'
            }
        persons_list = []
        for personid in personsid_list:
            persons_list.append(models.Person.objects.get(pk=personid))

        createNotification(persons_list, notification_type, description,
                        project_name=project_name, task_name=task_name)

        for person in persons_list:
            device = FCMDevice.objects.filter(user_id__exact = person.user.userid).first()
            if device is not None:
                device = FCMDevice.objects.get(user_id__exact = person.user.userid)
                device.send_message(title="OPX", body=push_message)
        
    except ObjectDoesNotExist as e:
        print(str(e))

    except ValidationError as e:
        print(dict(e))

    except IntegrityError as e:
        print(str(e))


def createNotification(persons_list, notification_type, description, project_name=None, task_name=None):
    """
    create a record in the notification table for each person in the persons list.

    If project_name is None, will set it null in database.

    If task_name is None, wiill set it null in database.
    """
    try:

        for person in persons_list:

            notification = Notification(
                notification_type=notification_type,
                person=person,
                description=description
            )
            if project_name:
                notification.project_name = project_name
            if task_name:
                notification.task_name = task_name
            notification.full_clean()
            notification.save()

    except ValidationError as e:
        print(dict(e))

    except IntegrityError as e:
        print(str(e))

@csrf_exempt
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getPersonNotifications(request):

    user = usuarioAutenticado(request)
    person = models.Person.objects.get(user__userid__exact = user.userid)

    notifications = models.Notification.objects.filter(person__pers_id__exact = person.pers_id).order_by('-notification_date')
    notifications = list(notifications.values())
    response = {
        'code': 200,
        'data': notifications,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

@csrf_exempt
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def deletePersonNotifications(request):
    with transaction.atomic():

        user = usuarioAutenticado(request)
        person = models.Person.objects.get(user__userid__exact = user.userid)
        query = "DELETE FROM opx.notification \
	            WHERE opx.notification.person_id  = '"+str(person.pers_id)+"';"
        with connection.cursor() as cursor:
            cursor.execute(query)
            data={
                'code': 200,
                'status': 'success',
                'notificaciones': [],
            }
        return JsonResponse(data, safe=False, status=data['code'])
