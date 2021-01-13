from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext
import shapely.geometry
import geopandas

from myapp import models

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

from myapp.view.utilidades import dictfetchall, usuarioAutenticado
from myapp.view.osm import detalleCartografia

from opc.opc_settings import settings
from myapp.view import(
    koboclient,
    tmclient,
    encuestaview,
)

# ============================ Encuestas ==========================
##
# @brief Recurso de almacenamiento de encuestas
# @param instrumento Instancia modelo Instrumento
# @param informacion dataset de encuestas a almacenar
# @param userid Identificación del usuario
# @param tareid Identificación de la tarea
# @return Diccionario
#
#@api_view(["POST"])
#@permission_classes((IsAuthenticated,))
def almacenarEncuestas(instrumento, informacion, person, task):

    try:
        with transaction.atomic():
            index_info = len(informacion)
            #for info in informacion:

            #try:
                #models.Survery.objects.get(koboid__exact=info['_uuid'])

            #except ObjectDoesNotExist:
            info = informacion[index_info]
            encuesta = models.Survery(
                instrument=instrumento, 
                koboid=info['_uuid'], 
                survery_content=json.dumps(info), 
                #userid=userid, (person)
                person=person,
                task=task)
            encuesta.full_clean()
            encuesta.save()

    except ValidationError as e:

        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

##
# @brief Revisión del estado de una encuesta
# @param request Instancia HttpRequest
# @param encuestaid Identificación de la encuesta
# @return cadena JSON
#


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def revisarEncuesta(request, encuestaid):

    try:
        encuesta = models.Survery.objects.get(pk=encuestaid)

        encuesta.survery_observation = request.POST.get('observacion')
        encuesta.survery_state = request.POST.get('estado')

        encuesta.full_clean()
        encuesta.save()

        response = {
            'code': 200,
            # 'encuesta': model_to_dict(encuesta),
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
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(response, status=response['code'], safe=False)

##
# @brief Plantilla de creación de Encuesta
# @param request Instancia HttpRequest
# @return Plantilla HTML
#
@permission_classes((IsAuthenticated,))
def creacionEncuestaView(request):

    return render(request, "instrumentos/creacion-encuesta.html")
