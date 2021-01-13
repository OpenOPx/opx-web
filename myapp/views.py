# from django.shortcuts import render
from datetime import datetime
import json
from myapp.view.proyecto import ROL_PROYECTISTA, ROL_SUPER_ADMIN
import os
import http.client
from passlib.context import CryptContext
import shapely.geometry
import geopandas

from myapp import models
from fcm_django.models import FCMDevice

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import (connection, transaction)
from django.db.utils import DataError, IntegrityError
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from myapp.view import (
    utilidades
)

from myapp.view.utilidades import dictfetchall, usuarioAutenticado


# Create your views here.

##
# Vista de Autenticación Dashboard
# @param request Instancia HttpRequest
# @return Plantilla Html
#


def loginView(request):

    return render(request, "auth/login.html")


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):

    try:

        username = request.POST.get("username")
        password = request.POST.get("password")
        fcm_token = request.POST.get('fcm_token')
        type_device = request.POST.get('type_device')

        if username is None or password is None:
            data = {
                'status': 'error',
                'message': 'Por favor especifique usuario y contraseña',
                'code': 400
            }

        else:
            user = models.User.objects.get(useremail__exact=username)
            person = models.Person.objects.get(user__userid__exact=user.userid)

            # .filter(password__exact = password)
            #user = authenticate(email=username, password=password)

            # Si el correo electrónico existe
            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )
            passwordVerification = pwd_context.verify(password, user.password)

            if(passwordVerification):

                # Generación de tokens
                refresh = RefreshToken.for_user(user)

                # Almacenando los permisos del usuario en la sesión
                request.session['permisos'] = []
                permisos = models.RolePermissionn.objects.filter(role__role_id__exact = person.role.role_id)
                for i in permisos:
                    request.session['permisos'].append(str(i.permissionn_id))

                # Consultando el nombre del rol del usuario autenticado
                rol = models.Role.objects.get(person__pers_id__exact = person.pers_id)
                data = {
                    'token': str(refresh.access_token),
                    'user': {
                        'userid':       user.userid, #Para web
                        'pers_id':       user.userid, #Para movil
                        'userfullname': person.pers_name+ " " + person.pers_lastname,
                        'useremail':    user.useremail,
                        'rol':          rol.role_name, #Para web
                        'role_name':          rol.role_name, #Para movil
                        'puntaje':      person.pers_score
                    },
                    'code': 200
                }
                if fcm_token is not None and type_device is not None:
                    device = FCMDevice.objects.filter(user_id__exact = user.userid).first()
                    if device is not None:
                        current_fcmtkn = device.registration_id
                        if current_fcmtkn != fcm_token:
                            device.registration_id = fcm_token
                            device.type=type_device
                            device.save()
                            #verificar sesiones activas y cerrarlas
                    else:
                        device = FCMDevice(
                            user=user,
                            registration_id=fcm_token,
                            type=type_device
                        )
                        device.save()
                else:
                    #login desde la web
                    ROL_SUPER_ADMIN = '8945979e-8ca5-481e-92a2-219dd42ae9fc'
                    ROL_PROYECTISTA = '628acd70-f86f-4449-af06-ab36144d9d6a'
                    print(person.role.role_id)
                    if(str(person.role.role_id) == ROL_SUPER_ADMIN or str(person.role.role_id) == ROL_PROYECTISTA):
                        print("if")
                        pass
                    else:
                        print("else")
                        data={
                            'code': 403,
                            'status': 'error',
                            'message': 'Acceso no permitido para ese usuario',
                        }
                # Puntaje esperado para llegar a rol proximo
                # Voluntario
                # if str(rol.rolid) == '0be58d4e-6735-481a-8740-739a73c3be86':
                #    data['user']['promocion'] = {
                #        'rol': "Validador",
                #       'puntaje': int(settings['umbral-validador'])
                #   }

                # Proyectista
                # elif str(rol.rolid) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
                #    data['user']['promocion'] = {
                #        'rol': "Proyectista",
                #        'puntaje': int(settings['umbral-proyectista'])
                #    }

            else:

                data = {
                    'status': 'error',
                    'message': 'Usuario y/o contraseña incorrecta',
                    'code': 404
                }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'message': 'Usuario y/o contraseña incorrecta',
            'code': 404
        }

    return JsonResponse(data, status=data['code'])


##
# @brief Recurso de listado de instrumentos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoTiposDeTareas(request):

    task_types = models.TaskType.objects.all().values()

    response = JsonResponse(list(task_types), safe=False)

    return response
