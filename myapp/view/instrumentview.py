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
    tmclient
)

##
# @brief Plantilla de Instrumentos
# @param request Instancia HttpRequest
# @return Plantilla HTML
#
@permission_classes((IsAuthenticated,))
def listadoInstrumentosView(request):
    return render(request, "instrumentos/listado.html")


# =============================== Instrumentos ===================

##
# @brief Recurso de listado de instrumentos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoInstrumentos(request):

    instrtipo = request.GET.get('instrtipo')

    if(instrtipo is None):

        instrumentos = models.Instrument.objects.all().values()

    else:

        instrumentos = models.Instrument.objects.filter(
            instrument_type__exact=instrtipo).values()

    response = JsonResponse(list(instrumentos), safe=False)

    return response

##
# @brief Recurso de almacenamiento de Instrumento
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoInstrumento(request):

    instrTipo = request.POST.get('instrtipo')
    instrNombre = request.POST.get('instrnombre')
    instrDescripcion = request.POST.get('instrdescripcion')
    areaInteres = request.POST.get('areaInteres')
    KOBO_INSTRUMENT = "1"
    TM_INSTRUMENT = "2"

    if(instrTipo is None):
        return JsonResponse({'status': 'error'}, status=400)

    if instrTipo == KOBO_INSTRUMENT:
        instrIdExterno = request.POST.get('instridexterno')

    elif instrTipo == TM_INSTRUMENT:
        instrIdExterno = tmclient.almacenarProyectoTM(
            instrNombre, json.loads(areaInteres))

        if not instrIdExterno:
            instrIdExterno = "12345"

    else:
        instrIdExterno = "12345"

    instrumento = models.Instrument(
        external_id=instrIdExterno,
        instrument_type=instrTipo,
        instrument_name=instrNombre,
        instrument_description=instrDescripcion,
        geojson=areaInteres)

    try:
        instrumento.full_clean()

        if instrumento.external_id == '12345':

            return JsonResponse({}, safe=False, status=500)

        else:

            instrumento.save()
            data = serializers.serialize('python', [instrumento])
            return JsonResponse(data, safe=False, status=201)

    except ValidationError as e:
        return JsonResponse(dict(e), safe=True, status=400)

##
# @brief Recurso para eliminación de instrumentos
# @param request Instancia HttpRequest
# @param instrid Identificación del Instrumento
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarInstrumento(request, instrid):

    try:
        instrumento = models.Instrument.objects.get(pk=instrid)
        #instrumento.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe=True, status=404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe=True, status=400)

##
# @brief Recurso de actualización de Instrumentos
# @param request Instancia HttpRequest
# @param instrid Identificación del Instrumento
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarInstrumento(request, instrid):

    try:
        instrumento = models.Instrument.objects.get(pk=instrid)

        #instrumento.instridexterno = request.POST.get('instridexterno')
        #instrumento.instrtipo = request.POST.get('instrument_type')
        instrumento.instrument_name = request.POST.get('instrument_name')
        instrumento.instrument_description = request.POST.get('instrument_description')

        instrumento.full_clean()

        instrumento.save()

        return JsonResponse(serializers.serialize('python', [instrumento]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:

        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)





##
# @brief Recurso para obtener información de instrumentos
# @param request Instancia HttpRequest
# @param id Indentificación del instrumento
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def informacionInstrumento(request, id):
    #TODO
    try:
        tarea = models.Task.objects.get(pk=id)
        #instrumento = models.Instrument.objects.get(pk=tarea.instrid)
        instrumento = tarea.instrument
        if instrumento.instrument_type == 1:

            informacion = koboclient.informacionFormularioKoboToolbox(
                instrumento.external_id)

            if(isinstance(informacion, dict)):

                #almacenarEncuestas(instrumento, informacion['info'])
                encuestasDB = models.Survery.objects.filter(
                    task__task_id__exact=tarea.task_id)
                encuestas = []

                for e in encuestasDB:
                    contenido = json.loads(e.survery_content) # posible error porque no define el key para el json
                    contenido['encuestaid'] = e.survery_id
                    contenido['estado'] = e.survery_state
                    contenido['observacion'] = e.survery_observation

                    encuestas.append(contenido)

                data = {
                    'status': 'success',
                    'code': 200,
                    'info': {
                        'campos': informacion['campos'],
                        'info': encuestas,
                        'tipoInstrumento': instrumento.instrument_type
                    },
                    'instrumento': model_to_dict(instrumento)
                }

            else:

                data = {
                    'status': 'error',
                    'code': 500
                }

        elif instrumento.instrument_type == 2:

            informacion = tmclient.informacionProyectoTM(instrumento.external_id)
            informacionMapeo = detalleCartografia(str(tarea.task_id))

            if(informacionMapeo['code'] == 200):
                geojson = informacionMapeo['geojson']
            else:
                geojson = "{}"

            if (isinstance(informacion, dict)):

                informacion['tipoInstrumento'] = instrumento.instrument_type

                data = {
                    'status': 'success',
                    'code': 200,
                    'info': informacion,
                    'geojson': geojson,
                    'instrumento': model_to_dict(instrumento)
                }

            else:

                data = {
                    'status': 'error',
                    'code': 500
                }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'code': 404
        }

    except ValidationError:

        data = {
            'status': 'error',
            'code': 400
        }

    return JsonResponse(data, status=data['code'])


##
# @brief Plantilla para información de Instrumento
# @param request Instancia HttpRequest
# @param id Identificación del instrumento
# @return Plantilla HTML
#
@permission_classes((IsAuthenticated,))
def informacionInstrumentoView(request, id):

    try:
        instrumento = models.Instrument.objects.get(pk=id)

        return render(request, "instrumentos/informacion.html", {'instrumento': instrumento})

    except ObjectDoesNotExist:
        return HttpResponse("", status=404)

    except ValidationError:
        return HttpResponse("", 400)

