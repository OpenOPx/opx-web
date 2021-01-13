
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

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
# ======================== Contextos ===============================

##
# @brief Recurso de listado de contextos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoContextos(request):
    contextos = models.Context.objects.all().values()
    return JsonResponse(list(contextos), safe = False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoContextosProyecto(request, proyid):

    try:
        models.Project.objects.get(proj_id=proyid)

        # Listado de IDS de contexto
        contextos = []
        contextosID = models \
                    .ProjectContext \
                    .objects \
                    .filter(proj_id=proyid)

        # Inserción de IDs en lista para consulta posterior
        for contexto in contextosID:
            contextos.append(str(contexto.context_id))

        # Consulta de contextos
        contextos = models.Context.objects.filter(ontext_id__in=contextos).values()

        response = {
            'code':         200,
            'contextos':    list(contextos),
            'status':       'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'status':   'error'
        }

    except ValidationError:
        response = {
            'code':     400,
            'status':   'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso de almacenamiento de contextos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoContexto(request):

    contexto = models.Context(
        context_description=request.POST.get('descripcion')
    )

    try:
        contexto.full_clean()

        contexto.save()

        data = {
            'status': 'success',
            'contexto': serializers.serialize('python', [contexto])[0],
            'code': 201
        }
    except ValidationError as e:
        data = {
            'status': 'error',
            'errors': dict(e),
            'code': 400
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de eliminación de contextos
# @param request Instancia HttpRequest
# @param contextoid Identificación del contexto
# @return cadena JSON
#
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarContexto(request, contextoid):

    proyecto_contexto = models.ProjectContext.objects.filter(context__context_id__exact = contextoid)
    proyecto_contexto = list(proyecto_contexto)

    if len(proyecto_contexto) > 0:
        raise ValueError("El contexto esta asociado a un proyecto")

    try:
        contexto = models.Context.objects.get(context_id = contextoid)

        contexto.delete()

        data = {
            'status': 'success',
            'code': 200
        }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'code': 404
        }

    except ValidationError:

        data = {
            'status': 'error',
            'message': 'Información inválida',
            'code': 400
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Recurso de actualización de contextos
# @param request Instancia HttpRequest
# @param contextoid Identificación del Contexto
# @return cadena JSON
#
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarContexto(request, contextoid):
    try:
        id = request.POST.get('context_id')
        contexto = models.Context.objects.get(context_id = id)

        contexto.context_description = request.POST.get('descripcion')

        contexto.full_clean()

        contexto.save()

        data = {
            'status': 'success',
            'contexto': serializers.serialize('python', [contexto])[0],
            'code': 200
        }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'code': 404
        }

    except ValidationError:

        data = {
            'status': 'error',
            'message': 'Información inválida',
            'code': 400
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Plantilla HTML de contextos
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoContextosView(request):

    return render(request, "contextos/listado.html")

# ======================== Datos de Contexto =======================

##
# @brief Convierte feature de Mapa a GeoJSON
# @param geometry Feature de Mapa - Puede ser Punto o Poligono
# @return GeoJSON
#
def geopandaGeojson(geometry):

    try:

        # shape = 'POINT (-76.5459307779999 3.4440059623)'.capitalize().split()
        # shape = 'POLYGON ([(0, 0), (0, 1), (1, 0)])'
        #geometry = 'POLYGON ((1059603.6619 869938.2576, 1059613.8392 869969.4889999999, 1059643.2931 869960.2558, 1059637.8753 869943.791, 1059633.082 869929.2239, 1059603.6619 869938.2576))'
        shape = geometry.capitalize().split()

        if shape[0] == 'Point':
            command = eval("shapely.geometry." + shape[0] + shape[1] + "," + shape[2])
            geojson = geopandas.GeoSeries(command).to_json()

        elif shape[0] == 'Polygon':

            coordenadas = []
            search = geometry.split('((', 1)[1].split('))')[0]
            puntos = search.split(', ')

            for p in puntos:
                coords = p.split()
                data = (float(coords[0]), float(coords[1]))
                coordenadas.append(data)

            polygon = shapely.geometry.Polygon(coordenadas)
            geojson = geopandas.GeoSeries(polygon).to_json()

        else:
            raise ValidationError({'csv': 'Formato de archivo no valido'})

    except ValueError as e:
        raise ValidationError({'csv': e})

    return geojson


##
# @brief Recurso de listado de datos de contexto
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def listadoDatosContextoCompleto(request):

    contextosList = []

    contextos = models.Context.objects.all()

    if contextos:

        for c in contextos:

            datosContexto = models.DataContext.objects.filter(context__exact = c.context_id)

            if datosContexto:

                contextosList.append({
                    'contextoid': c.context_id,
                    'contexto': c.context_description,
                    'datos': list(datosContexto.values())
                })

    data = {
        'code': 200,
        'contextos': contextosList,
        'status': 'success'
    }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de listado de datos de contexto por contexto
# @param request Instancia HttpRequest
# @param contextoid Identificación del Contexto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDatosContexto(request, contextoid):

    datosContexto = models.DataContext.objects.filter(context__exact = contextoid).values()

    data = {
        'status': 'success',
        'datosContexto': list(datosContexto),
        'code': 200
    }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de almacenamiento de datos de contexto
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenarDatoContexto(request):

    # hdxtag = request.POST.get('hdxtag')
    # datavalor = " "
    # datatipe = 1
    # datosContexto = models.DatosContexto(hdxtag = hdxtag, datavalor = datavalor, datatipe = datatipe, contextoid = contextoid)

    # with open('/home/vagrant/code/opc-webpack/myapp/static/uploads/datoscontexto/' + str(datosContexto.dataid) + '.csv', 'wb+') as destination:
    #     for chunk in file.chunks():
    #         destination.write(chunk)

    try:

        if "file" in request.FILES.keys():
            file = request.FILES['file']

            if file.content_type == "text/csv" or file.content_type == "application/vnd.ms-excel":

                datosContexto = []

                # Obteniendo contentido del archivo
                fileData = str(file.read(), "utf-8")

                #Obtener lineas del archivo
                lines = fileData.splitlines()

                #leer cada linea
                for line in lines[1:]:

                   # Almacenando información en un diccionario
                   data = line.split(';')

                   #Asignación de fecha/hora en caso tal esten definidos en el archivo plano
                   try:
                    fecha = data[5]
                    hora = data[6]

                   except IndexError:
                       fecha = None
                       hora = None

                   datosContexto.append({
                    'hdxtag': data[0],
                    'data_description': data[1],
                    'data_value': data[2],
                    'data_type': data[3],
                    'data_geojson': geopandaGeojson(data[4]),
                    'data_date': fecha,
                    'data_time': hora
                   })

                try:
                    with transaction.atomic():

                      contextoid = request.POST.get('context_id')

                      for dt in datosContexto:
                         datosContexto = models.DataContext(hdxtag=dt['hdxtag'], data_value=dt['data_value'], data_type= dt['data_type'], context_id=contextoid, data_description = dt['data_description'], geojson = dt['geojson'], data_date=dt['data_date'], data_time=dt['data_time'])
                         datosContexto.full_clean()
                         datosContexto.save()

                    data = {
                       'code': 200,
                        'status': 'success'
                    }

                except ValidationError as e:

                   data = {
                       'code': 400,
                       'errors': dict(e)
                   }

            else:

                data = {
                    'status': 'error',
                    'errors': 'El tipo de archivo no es permitido',
                    'code': 400
                }

        else:

            data = {
                'status': 'error',
                'errors': 'No se encontro ningun archivo',
                'code': 400
            }


    except ValidationError as e:

        data = {
            'status': 'error',
            'errors': dict(e),
            'code': 400
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de eliminación de datos de contexto
# @param request Instancia HttpRequest
# @param dataid Identificación de dato de contexto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarDatoContexto(request, dataid):

    try:
        datoContexto = models.DataContext.objects.get(data_id = dataid)

        datoContexto.delete()

        #os.remove("/home/vagrant/code/opc-webpack/myapp/static/uploads/datoscontexto/" + dataid + ".csv")

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de actualización de datos de contexto
# @param request Instancia HttpRequest
# @param dataid Identificación de dato de contexto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarDatoContexto(request, dataid):
    try:
        datoContexto = models.DatosContexto.objects.get(data_id=dataid)

        datoContexto.hdxtag = request.POST.get('hdxtag')
        datoContexto.data_description = request.POST.get('descripcion')
        datoContexto.data_value = request.POST.get('datavalor')
        datoContexto.data_type = request.POST.get('datatipe')

        datoContexto.full_clean()

        # if "file" in request.FILES.keys():
        #
        #     file = request.FILES['file']
        #
        #     if file.content_type != "text/csv" and file.content_type != "application/vnd.ms-excel":
        #
        #         data = {
        #             'status': 'error',
        #             'errors': 'El tipo de archivo no es permitido',
        #             'code': 400
        #         }
        #         raise ValidationError(data)
        #
        #     with open('/home/vagrant/code/opc-webpack/myapp/static/uploads/datoscontexto/' + str(
        #             datoContexto.dataid) + '.csv', 'wb+') as destination:
        #         for chunk in file.chunks():
        #             destination.write(chunk)

        datoContexto.save()

        data = {
            'code': 200,
            'datoContexto': serializers.serialize('python', [datoContexto])[0],
            'status': 'success'
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Plantilla de datos de contexto
# @param request Instancia HttpRequest
# @param contextoid Identificación del contexto
# @return Plantilla HTML
#
def listadoDatosContextoView(request, contextoid):

    try:
        contexto = models.Context.objects.get(context_id = contextoid)
        return render(request, "contextos/datos-contexto.html", {'contexto': contexto})

    except ObjectDoesNotExist:
        code = 404

    except ValidationError:
        code = 400

    return HttpResponse("", status = code)
