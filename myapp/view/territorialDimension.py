from datetime import datetime
import json
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
from django.http import HttpResponse, HttpResponseBadRequest, request
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


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDimensionesBarrios(request):
    """
    Retorna el listado de dimensiones territoriales precargadas de acuerdo al tipo
    """
    DIMENSION_TIPO_URBANA = '35b0b478-9675-45fe-8da5-02ea9ef88f1b'
    query = "select dim.dimension_id, dim.dimension_name \
            from opx.territorial_dimension as dim \
            where dim.preloaded = '1' and dim.dimension_type_id = '"+DIMENSION_TIPO_URBANA+"'"
    with connection.cursor() as cursor:
        cursor.execute(query)
        barriosDimensions = dictfetchall(cursor)

    return JsonResponse(barriosDimensions, safe = False)

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getDimensionPreloaded(request, dimension_id):
    dimension = models.TerritorialDimension.objects.get(pk=dimension_id)
    dimension = serializers.serialize('python', [dimension])[0]

    return JsonResponse(dimension, safe=False)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def updateGeojson(request, dimension_id):

    geojson = request.POST.get('geojson')
    data = {}

    dimension = models.TerritorialDimension.objects.get(pk = dimension_id)
    if geojson is not None:
        dimension.dimension_geojson = geojson
        dimension.full_clean()
        dimension.save()
        data = {
            'code': 200,
            'status': 'success',
            'dimension': serializers.serialize('python', [dimension]),
        }
    else:
        data = {
            'code': 400,
            'status': 'error',
        }

    return JsonResponse(data, status=data['code'])

