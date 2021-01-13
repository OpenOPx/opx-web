
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
from myapp.view.utilidades import usuarioAutenticado, dictfetchall

##
# @brief Plantilla de decisiones
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoDecisionesView(request):
    return render(request, "decisiones/listado.html")

##
# @brief Recurso de listado de decisiones
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDecisiones(request):
    with connection.cursor() as cursor:
        cursor.execute("select opx.decision.decs_id, opx.decision.decs_description, opx.decision.decs_name from opx.decision order by opx.decision.decs_name ASC")
        columns = dictfetchall(cursor)
        return JsonResponse(columns, safe = False)

     #decisiones = models.Decision.objects.all().values()
     #return JsonResponse(list(decisiones), safe = False)


##
# @brief Recurso de almacenamiento de decisiones
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenarDecision(request):
    userid = usuarioAutenticado(request).userid

    decision = models.Decision(
        decs_name = request.POST.get('decs_name'),
        decs_description = request.POST.get('decs_description')
    )

    try:
        with transaction.atomic():
            decision.full_clean()
            decision.save()
        
            data = serializers.serialize('python', [decision])
        return JsonResponse(data, safe = False, status = 201)

    except ValidationError as e:
        return JsonResponse(dict(e), safe = True, status = 400)

##
# @brief Recurso de eliminación de decisiones
# @param request Instancia HttpRequest
# @param desiid Identificación de la decisión
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarDecision(request, desiid):
    
    proyecto_decision = models.ProjectDecision.objects.filter(decision__decs_id__exact = desiid)
    proyecto_decision = list(proyecto_decision.values())

    if len(proyecto_decision) > 0:
        raise ValueError("La decision esta asociada a un proyecto")

    try:
        decision = models.Decision.objects.get(pk = desiid)
        decision.delete()
        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'La decision no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de actualización de decisiones
# @param request Instancia HttpRequest
# param desiid Identificación de la decisión
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarDecision(request, desiid):

    try:
        with transaction.atomic():
            decision = models.Decision.objects.get(pk=desiid)

            decision.decs_description = request.POST.get('decs_description')
            decision.decs_name = request.POST.get('decs_name')

            decision.full_clean()

            decision.save()

        return JsonResponse(serializers.serialize('python', [decision]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

        