from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.shortcuts import render
from myapp import models

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp import models

from myapp.models import ProjectType

##
# @brief Recurso que provee el listado de Tipos de proyecto disponibles
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoTiposProyecto(request):

    tiposProyecto = models.ProjectType.objects.all().values()

    response = {
        'code': 200,
        'data': list(tiposProyecto),
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso de almacenamiento de Tipos de proyecto
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def almacenamientoTiposProyecto(request):

    try:
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        tipoProyecto = models.ProjectType(projtype_name=nombre, projtype_description=descripcion)
        tipoProyecto.full_clean()
        tipoProyecto.save()

        response = {
            'code': 201,
            'data': model_to_dict(tipoProyecto),
            'status': 'success'
        }

    except ValidationError as e:
        response = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso de actualización de Tipos de proyecto
# @param request Instancia HttpRequest
# @param tiproid Identificación del tipo de proyecto
# @return cadena JSON
#
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edicionTipoProyecto(request, tiproid):

    try:
        tipoProyecto = ProjectType.objects.get(projtype_id=tiproid)

        tipoProyecto.projtype_name = request.POST.get('nombre')
        tipoProyecto.projtype_description = request.POST.get('descripcion')

        tipoProyecto.full_clean()
        tipoProyecto.save()

        response = {
            'code': 200,
            'data': model_to_dict(tipoProyecto),
            'status': 'success'
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
# @brief Recurso de eliminación de Tipos de proyecto
# @param request Instancia HttpRequest
# @param tiproid Identificación del tipo de proyecto
# @return cadena JSON
#
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def eliminarTipoProyecto(request, tiproid):

    try:
        tipoProyecto = ProjectType.objects.get(projtype_id=tiproid)
        tipoProyecto.delete()

        response = {
            'code': 200,
            'status': 'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }


    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Función que provee una plantilla HTML para gestión de Tipos de proyecto
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def tiposProyectoView(request):

    return render(request, "proyectos/tipos-proyecto.html")