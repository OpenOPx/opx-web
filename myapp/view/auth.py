from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext
import string
import random

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import connection
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

##
# @brief Plantilla de solicitud de Recuperación de Contraseña
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def passwordReset(request):

    return render(request, "auth/password-reset.html")

##
# @brief Envio de Notificación de Correo para recuperación de contraseña
# @param request instancia HttpRequest
# @return Diccionario
#
@api_view(["POST"])
@permission_classes((AllowAny,))
def passwordResetVerification(request):

    try:

        email = request.POST.get('email')

        if email is None:

            data = {
                'code': 400,
                'status': 'error',
                'message': 'No has proporcionado una cuenta de correo'
            }

        else:

            # Consulta de Usuario
            usuario = models.User.objects.get(useremail__exact = email)
            person = models.Person.objects.get(user__userid__exact = usuario.userid)

            # Asunto
            subject = "Recuperación de contraseña OPX"

            # Generación de Token
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))

            # Estableciendo token a usuario
            usuario.usertoken = token
            usuario.save()

            # Mensaje del correo
            message = '<h1><span style="color: #3366ff;"><span style="color: #000000;">Solicitud de cambio de </span> \
                        <span style="color: #2b2301;"><span style="color: #ff0000;"><span style="color: #000000;">contrase&ntilde;a!</span></span></span></span></h1> \
                        <h2 style="color: #2e6c80;">'+person.pers_name +',</h2> \
                        <p>Se ha solicitado el restablecmiento de tu contrase&ntilde;a. Para continuar con el proceso, por favor de click en el siguiente enlace \
                        <span style="background-color: #3366ff; color: #ffffff; display: inline-block; padding: 3px 10px; font-weight: bold; border-radius: 5px;"> \
                        <a style="background-color: #3366ff; color: #ffffff;" href="'+settings.URL_APP+'auth/password-reset/'+token+'">Solicitar contrase&ntilde;a</a></span>&nbsp;</p>\
                        <p>Si tu no has hecho esta solicitud, por favor has caso omiso de este mensaje.</p> \
                        <p>&nbsp;</p> \
                        <h1><span style="color: #3366ff;"><strong>Open OPX</strong></span></h1> \
                        <p>&nbsp;</p>'
            # Envío de correo electrónico
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=message
            )

            data = {
                'code': 200,
                'status': 'success'
            }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error',
            'message': 'No se encontro una cuenta con el correo proporcionado'
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Plantilla de Cambio de Contraseña
# @param request instancia HttpRequest
# @param token Token de Cambio de Contraseña
# @return plantilla HTML
#
def passwordResetConfirmation(request, token):

    try:
        usuario = models.User.objects.get(usertoken__exact = token)

        status = True

    except ObjectDoesNotExist:

        status = False

    data = {
        'status': status,
        'token': token
    }

    return render(request, "auth/password-reset-confirmation.html", context = data)

##
# @brief Plantilla para cambio de contraseña
# @param request instancia HttpRequest
# @return Diccionario
#
@api_view(["POST"])
@permission_classes((AllowAny,))
def passwordResetDone(request):

    try:

        token = request.POST.get('token')
        password = request.POST.get('password')

        if token is None or password is None:

            data = {
                'code': 400,
                'message': 'La contraseña y/o el token no fueron proveidos',
                'status': 'error'
            }

        else:

            # Eliminación de token y modificación de contraseña
            usuario = models.User.objects.get(usertoken__exact=token)

            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )

            usuario.password = pwd_context.encrypt(password)
            usuario.usertoken = None
            usuario.save()

            data = {
                'code': 200,
                'status': 'success'
            }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'])