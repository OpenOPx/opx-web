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

# ==================== Tasking Manager ==================

##
# @brief Almacenamiento de Proyecto de Mapeo en Tasking Manager
# @param nombre nombre del Proyecto
# areaInteres geoJSON que describe el área de trabajo de un proyecto de Mapeo
# @return Diccionario
#
def almacenarProyectoTM(nombre, areaInteres):

    headers = {
        'Authorization': settings['tm-token'],
        'Accept-Language': 'en',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    info = {
        "areaOfInterest": {
            "type": "FeatureCollection",
            "features": [areaInteres]
        },
        "projectName": nombre,
        "arbitraryTasks": True
    }

    client = http.client.HTTPConnection(settings['tm'], int(
        settings['tm-puerto']), timeout=int(settings['timeout-request']))
    client.request('PUT', '/api/v1/admin/project', json.dumps(info), headers)
    response = client.getresponse()

    if response.status == 201:
        return json.loads(response.read())['projectId']

    else:
        return False

##
# @brief Obtención de información de detalle de un Proyecto de Mapeo de Tasking Manager
# @param id Identificación del proyecto de Mapeo Tasking Manager
# @return Diccionario
#


def informacionProyectoTM(id):
    headers = {
        'Authorization': settings['tm-token']
    }

    client = http.client.HTTPConnection(settings['tm'], int(
        settings['tm-puerto']), timeout=int(settings['timeout-request']))
    client.request('GET', '/api/v1/project/' + id, {}, headers)
    response = client.getresponse()

    if (response.status != 200):

        data = False

    else:

        data = json.loads(response.read())

    return data
