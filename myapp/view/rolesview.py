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
from myapp.view.utilidades import dictfetchall, usuarioAutenticado

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from myapp import models

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
# ============================ Roles =============================

##
# @brief Recurso de Listao de Roles
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoRoles(request):

    roles = models.Role.objects.filter(isactive__exact=1).values()

    data = {
        'code': 200,
        'roles': list(roles),
        'status': 'success'
    }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de almacenamiento de Roles
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoRol(request):

    rolName = request.POST.get('rolname')
    rolDescripcion = request.POST.get('roldescripcion')   
    rolEstado = 1

    rol = models.Rol(role_name = rolName, role_description = rolDescripcion, isactive = rolEstado)

    try:
        rol.full_clean()

        rol.save()
        data = serializers.serialize('python', [rol])
        return JsonResponse(data, safe = False, status = 201)

    except ValidationError as e:
        return JsonResponse(dict(e), safe = True, status = 400)

##
# @brief Recurso de eliminación de Roles
# @param request Instancia HttpRequest
# @param rolid Identificación del Rol
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarRol(request, rolid):

    try:
        rol = models.Role.objects.get(pk = rolid)

        rol.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de actualización de Roles
# @param request Instancia HttpRequest
# @param rolid Identificación del Rol
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarRol(request, rolid):
    try:
        rol = models.Role.objects.get(pk=rolid)

        rol.role_name = request.POST.get('rolname')
        rol.role_description = request.POST.get('roldescripcion')        
        #rol.isactive = request.POST.get('rolestado') YA DIRÁ LA URL SI LA PONGO O NO

        rol.full_clean()

        rol.save()

        return JsonResponse(serializers.serialize('python', [rol]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

##
# @brief Plantilla de Roles
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoRolesView(request):

    return render(request, "roles/listado.html")

##
# @brief Plantilla de Funcionalidades del sistema para un rol
# @param request Instancia HttpRequest
# @param rolid Identificación del rol
# @return cadena JSON
#
def permisosRolView(request, rolid):

    try:
        rol = models.Role.objects.get(role_id__exact = rolid)

        return render(request, "roles/permisos.html", {'rol': rol})

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", status = 400)

# ========================= Funciones Rol =========================

##
# @brief Recurso de listado de Funciones del Sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoAcciones(request):

    acciones = models.Permissionn.objects.all().values()

    return JsonResponse(list(acciones), safe = False)

##
# @brief Recurso de listado de Funciones del Sistema para un rol
# @param request Instancia HttpRequest
# @param rolid Identificación del rol de usuario
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoFuncionesRol(request, rolid):

    with connection.cursor() as cursor:

        cursor.execute("select opx.role_permissionn.role_id, opx.permissionn.perm_id, opx.permissionn.perm_name from opx.role_permissionn inner join opx.permissionn on opx.role_permissionn.permissionn_id = opx.permissionn.perm_id where opx.role_permissionn.role_id = %s", [rolid])

        columns = dictfetchall(cursor)

        return JsonResponse(columns, safe = False)

##
# @brief Recurso para añadir Funciones del Sistema a un rol
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoFuncionRol(request):

    rolID = request.POST.get('rolid')
    accionID = request.POST.get('accionid')
  
    roles = models.Role.objects.get(role_id = rolID)
    permmisionn= models.Permissionn.objects.get(perm_id = accionID)

    funcionRol = models.RolePermissionn(role = roles, permissionn = permmisionn)

    try:
        funcionRol.full_clean()

        funcionRol.save()
        data = serializers.serialize('python', [funcionRol])
        return JsonResponse(data, safe = False, status = 201)

    except ValidationError as e:
        return JsonResponse(dict(e), safe = True, status = 400)

##
# @brief Recurso para eliminar Funciones del Sistema a un Rol
# @param request Instancia HttpRequest
# @param funcrolid Identificación de asignación de funcion del sistema a un rol
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarFuncionRol(request, funcrolid):
    roleid = request.data['id']

    try:
        funcionRol = models.RolePermissionn.objects.filter(permissionn_id = funcrolid).filter(role_id = roleid)

        funcionRol.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de actualización de Funcion del Sistema a un rol
# @param request Instancia HttpRequest
# @param funcrolid Identificación de asignación de funcion del sistema a un rol
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarFuncionRol(request, funcrolid):

    try:
        funcionRol = models.RolePermissionn.objects.get(pk=funcrolid)

        #funcionRol.rolid = request.POST.get('rolid')
        funcionRol.actionid = request.POST.get('actionid')
        #funcionRol.funcrolestado = request.POST.get('funcrolestado')
        #funcionRol.funcrolpermiso = request.POST.get('funcrolpermiso')

        funcionRol.full_clean()

        funcionRol.save()

        return JsonResponse(serializers.serialize('python', [funcionRol]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:

        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

