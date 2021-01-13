from datetime import date

from django.conf import settings
from django.core import serializers
from django.db import connection
from django.forms.models import model_to_dict
from django.http.response import JsonResponse, HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError

from myapp.models import Contextualizacion, Conflictividad, Usuario
from myapp.view.utilidades import dictfetchall

##
# @brief Indicadores de Conflictivades Por Categorias
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def categorizacion(request):

    try:
        barrioUbicacion = request.GET.get('barrioUbicacion')
        barrioSeleccion = request.GET.get('barrioSeleccion')
        year = request.GET.get('year')

        if request.META['HTTP_AUTHORIZATION'] != 'null':

            # Decodificando el access token
            tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                        settings.SIMPLE_JWT['VERIFYING_KEY'])
            tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

            # consultando el usuario
            user = User.objects.get(pk=tokenDecoded['user_id'])
            edadUsuario = calculoEdad(user.fecha_nacimiento)

        if barrioUbicacion is not None and barrioSeleccion is not None and year is not None:

            conflictividades = Conflictividad.objects.all()
            data = []

            for conf in conflictividades:

                queryIndicadorCiudad = "select SUM(t.cantidad) as count from \
                                        (select * from opx.contextualizaciones \
                                        where (confid = '{0}') \
                                        and (fecha_hecho between '{1}-01-01' and '{1}-12-31')) t;" \
                                        .format(conf.confid, year)

                queryIndicadorUbicacion = "select SUM(t.cantidad) as count from \
                                        (select * from opx.contextualizaciones \
                                        where confid = '{0}' \
                                        and barrioid = '{1}' \
                                        and (fecha_hecho between '{2}-01-01' and '{2}-12-31')) t;" \
                                        .format(conf.confid, barrioUbicacion, year)

                queryIndicadorSeleccion = "select SUM(t.cantidad) as count from \
                                           (select * from opx.contextualizaciones \
                                           where confid = '{0}' \
                                           and barrioid = '{1}' \
                                           and (fecha_hecho between '{2}-01-01' and '{2}-12-31')) t;" \
                                          .format(conf.confid, barrioSeleccion, year)

                if 'user' in locals():
                    queryIndicadorPerfil = "select SUM(t.cantidad) as count from \
                                               (select * from opx.contextualizaciones \
                                               where confid = '{0}' \
                                               and barrioid = {1} \
                                               and generoid = '{2}' \
                                               and nivelid = '{3}' \
                                               and edad = {4} \
                                               and (fecha_hecho between '{5}-01-01' and '{5}-12-31')) t;" \
                                               .format(conf.confid, user.barrioid, user.generoid, user.nivel_educativo_id, edadUsuario, year)



                with connection.cursor() as cursor:
                    cursor.execute(queryIndicadorCiudad)
                    indicadorCiudad = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    cursor.execute(queryIndicadorUbicacion)
                    indicadorUbicacion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    cursor.execute(queryIndicadorSeleccion)
                    indicadorSeleccion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    if 'user' in locals():
                        cursor.execute(queryIndicadorPerfil)
                        indicadorPerfil = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    if(indicadorCiudad != 0):
                        indicadorPromedio = indicadorCiudad / bisiesto(int(year))
                    else:
                        indicadorPromedio = 0

                indicadores = {
                    'conflictividad': model_to_dict(conf),
                    'indicadores': {
                        'ciudad': indicadorCiudad,
                        'ubicacion': indicadorUbicacion,
                        'seleccion': indicadorSeleccion,
                        'promedio': indicadorPromedio
                    },
                }

                if 'user'in locals():
                    indicadores['indicadores']['perfil'] = indicadorPerfil

                data.append(indicadores)

                response = {
                    'code': 200,
                    'data': data,
                    'status': 'success'
                }

        else:

            response = {
                'code': 400,
                'status': 'error'
            }

    except(IndexError):
        response = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:
        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }


    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Indicadores de conflictividades por Año
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def todo(request):

    try:

        barrioUbicacion = request.GET.get('barrioUbicacion')
        barrioSeleccion = request.GET.get('barrioSeleccion')

        if request.META['HTTP_AUTHORIZATION'] != 'null':

            # Decodificando el access token
            tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                        settings.SIMPLE_JWT['VERIFYING_KEY'])
            tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

            # consultando el usuario
            user = User.objects.get(pk=tokenDecoded['user_id'])
            edadUsuario = calculoEdad(user.fecha_nacimiento)


        if barrioUbicacion is not None and barrioSeleccion is not None:

            anioInicial = 2010
            anioFinal = 2019
            anios = []

            count = anioInicial

            conflictividadesCiudad = []
            conflictividadesUbicacion = []
            conflictividadesSeleccion = []
            conflictividadesPerfil = []

            while count <= anioFinal:

                anios.append(count)

                queryIndicadorCiudad = "SELECT SUM(t.cantidad) as count FROM (" \
                        "SELECT * FROM opx.contextualizaciones " \
                        "WHERE fecha_hecho between '{0}-01-01' and '{0}-12-31') t" \
                        .format(count)

                queryIndicadorUbicacion = "SELECT SUM(t.cantidad) as count FROM (" \
                        "SELECT * FROM opx.contextualizaciones " \
                        "WHERE barrioid = {1} and " \
                        "(fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                        .format(count, barrioUbicacion)

                queryIndicadorSeleccion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE barrioid = {1} and " \
                                          "(fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                                          .format(count, barrioSeleccion)

                if 'user' in locals():
                    queryIndicadorPerfil = "SELECT SUM(t.cantidad) as count FROM (" \
                                           "SELECT * FROM opx.contextualizaciones " \
                                           "WHERE barrioid = {1} " \
                                           "and generoid = '{2}' " \
                                           "and nivelid = '{3}' " \
                                           "and edad = {4} " \
                                           "and (fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                                           .format(count, user.barrioid, user.generoid, user.nivel_educativo_id, edadUsuario)

                with connection.cursor() as cursor:

                    # Indicador Ciudad
                    cursor.execute(queryIndicadorCiudad)
                    indicadorCiudad = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesCiudad.append(indicadorCiudad)

                    # Indicador Ubicación
                    cursor.execute(queryIndicadorUbicacion)
                    indicadorUbicacion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesUbicacion.append(indicadorUbicacion)

                    # Indicador Selección
                    cursor.execute(queryIndicadorSeleccion)
                    indicadorSeleccion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesSeleccion.append(indicadorSeleccion)

                    if 'user' in locals():
                        # Indicador Perfil
                        cursor.execute(queryIndicadorPerfil)
                        indicadorPerfil = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                        conflictividadesPerfil.append(indicadorPerfil)

                count += 1

            data = {
                'labels': anios,
                'datasets': [
                    {
                        'label': 'ciudad',
                        'fill': False,
                        'borderColor': 'orange',
                        'data': conflictividadesCiudad
                    },
                    {
                        'label': 'Ubicación',
                        'fill': False,
                        'borderColor': 'blue',
                        'data': conflictividadesUbicacion
                    },
                    {
                        'label': 'Selección',
                        'fill': False,
                        'borderColor': 'green',
                        'data': conflictividadesSeleccion
                    }
                ]
            }

            if 'user' in locals():

                totalConflictividadesPerfil = 0

                for cp in conflictividadesPerfil:
                    totalConflictividadesPerfil =  totalConflictividadesPerfil + cp

                data['datasets'].append({
                    'label': 'Perfil',
                    'fill': False,
                    'borderColor': 'red',
                    'data': conflictividadesPerfil,
                    'promedio': totalConflictividadesPerfil / len(conflictividadesPerfil)
                })

            response = {
                'code': 200,
                'data': data,
                'status': 'success'
            }

        else:
            response = {
                'code': 400,
                'status': 'error'
            }

    except(IndexError):

        response = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:

        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Indicadores de conflictividades por Mes
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def mensual(request):

    try:

        barrioUbicacion = request.GET.get('barrioUbicacion')
        barrioSeleccion = request.GET.get('barrioSeleccion')
        year = request.GET.get('year')

        if request.META['HTTP_AUTHORIZATION'] != 'null':

            # Decodificando el access token
            tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                        settings.SIMPLE_JWT['VERIFYING_KEY'])
            tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

            # consultando el usuario
            user = User.objects.get(pk=tokenDecoded['user_id'])
            edadUsuario = calculoEdad(user.fecha_nacimiento)

        if barrioUbicacion is not None and barrioSeleccion is not None and year is not None:

            meses = [
                {
                    'label': 'Enero',
                    'value': '01',
                    'lastDay': '31'
                },
                {
                    'label': 'Febrero',
                    'value': '02',
                    'lastDay': bisiesto(int(year), anio=False, mes=True)
                },
                {
                    'label': 'Marzo',
                    'value': '03',
                    'lastDay': '31'
                },
                {
                    'label': 'Abril',
                    'value': '04',
                    'lastDay': '30'
                },
                {
                    'label': 'Mayo',
                    'value': '05',
                    'lastDay': '31'
                },
                {
                    'label': 'Junio',
                    'value': '06',
                    'lastDay': '30'
                },
                {
                    'label': 'Julio',
                    'value': '07',
                    'lastDay': '31'
                },
                {
                    'label': 'Agosto',
                    'value': '08',
                    'lastDay': '31'
                },
                {
                    'label': 'Septiembre',
                    'value': '09',
                    'lastDay': '30'
                },
                {
                    'label': 'Octubre',
                    'value': '10',
                    'lastDay': '31'
                },
                {
                    'label': 'Noviembre',
                    'value': '11',
                    'lastDay': '30'
                },
                {
                    'label': 'Diciembre',
                    'value': '12',
                    'lastDay': '31'
                }
            ]

            conflictividadesCiudad = []
            conflictividadesUbicacion = []
            conflictividadesSeleccion = []
            conflictividadesPerfil = []

            for mes in meses:

                queryIndicadorCiudad = "SELECT SUM(t.cantidad) as count FROM (" \
                                       "SELECT * FROM opx.contextualizaciones " \
                                       "WHERE fecha_hecho between '{0}-{1}-01' and '{0}-{1}-{2}') t" \
                                        .format(year, mes['value'], mes['lastDay'])

                queryIndicadorUbicacion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE barrioid = {3} and " \
                                          "(fecha_hecho between '{0}-{1}-01' and '{0}-{1}-{2}')) t" \
                                          .format(year, mes['value'], mes['lastDay'], barrioUbicacion)

                queryIndicadorSeleccion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE barrioid = {3} and " \
                                          "(fecha_hecho between '{0}-{1}-01' and '{0}-{1}-{2}')) t" \
                                          .format(year, mes['value'], mes['lastDay'], barrioSeleccion)

                if 'user' in locals():

                    queryIndicadorPerfil = "SELECT SUM(t.cantidad) as count FROM (" \
                                           "SELECT * FROM opx.contextualizaciones " \
                                           "WHERE barrioid = {3} " \
                                           "and generoid = '{4}' " \
                                           "and nivelid = '{5}' " \
                                           "and edad = {6} " \
                                           "and (fecha_hecho between '{0}-{1}-01' and '{0}-{1}-{2}')) t" \
                                           .format(year, mes['value'], mes['lastDay'], user.barrioid, user.generoid, user.nivel_educativo_id, edadUsuario)

                with connection.cursor() as cursor:

                    #Indicador Ciudad
                    cursor.execute(queryIndicadorCiudad)
                    indicadorCiudad = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesCiudad.append(indicadorCiudad)

                    #Indicador Ubicación
                    cursor.execute(queryIndicadorUbicacion)
                    indicadorUbicacion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesUbicacion.append(indicadorUbicacion)

                    #Indicador Selección
                    cursor.execute(queryIndicadorSeleccion)
                    indicadorSeleccion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesSeleccion.append(indicadorSeleccion)

                    if 'user' in locals():
                        #Indicador Perfil
                        cursor.execute(queryIndicadorPerfil)
                        indicadorPerfil = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                        conflictividadesPerfil.append(indicadorPerfil)

            data = {
                'labels': [m['label'] for m in meses],
                'datasets': [
                    {
                        'label': 'ciudad',
                        'fill': False,
                        'borderColor': 'orange',
                        'data': conflictividadesCiudad
                    },
                    {
                        'label': 'Ubicación',
                        'fill': False,
                        'borderColor': 'blue',
                        'data': conflictividadesUbicacion
                    },
                    {
                        'label': 'Selección',
                        'fill': False,
                        'borderColor': 'green',
                        'data': conflictividadesSeleccion
                    }
                ]
            }

            if 'user' in locals():

                data['datasets'].append({
                    'label': 'Perfil',
                    'fill': False,
                    'borderColor': 'red',
                    'data': conflictividadesPerfil
                })

            response = {
                'code': 200,
                'data': data,
                'status': 'success'
            }

        else:
            response = {
                'code': 400,
                'status': 'error'
            }

    except(IndexError):

        response = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:

        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Indicadores de conflictividades por Semana
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def semanal(request):

    try:

        barrioUbicacion = request.GET.get('barrioUbicacion')
        barrioSeleccion = request.GET.get('barrioSeleccion')
        year = request.GET.get('year')

        if request.META['HTTP_AUTHORIZATION'] != 'null':
            # Decodificando el access token
            tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                        settings.SIMPLE_JWT['VERIFYING_KEY'])
            tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

            # consultando el usuario
            user = User.objects.get(pk=tokenDecoded['user_id'])
            edadUsuario = calculoEdad(user.fecha_nacimiento)

        if barrioUbicacion is not None and barrioSeleccion is not None and year is not None:

            semana = [
                {
                    'label': 'Domingo',
                    'value': 1
                },
                {
                    'label': 'Lunes',
                    'value': 2
                },
                {
                    'label': 'Martes',
                    'value': 3
                },
                {
                    'label': 'Miercoles',
                    'value': 4
                },
                {
                    'label': 'Jueves',
                    'value': 5
                },
                {
                    'label': 'Viernes',
                    'value': 6
                },
                {
                    'label': 'Sabado',
                    'value': 7
                }
            ]

            conflictividadesCiudad = []
            conflictividadesUbicacion = []
            conflictividadesSeleccion = []
            conflictividadesPerfil = []

            for sem in semana:

                queryIndicadorCiudad = "SELECT SUM(t.cantidad) as count FROM (" \
                                       "SELECT * FROM opx.contextualizaciones " \
                                       "WHERE dia = {1} and " \
                                       "(fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                                       .format(year, sem['value'])

                queryIndicadorUbicacion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE dia = {1} and " \
                                          "barrioid = {2} and " \
                                          "(fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                                          .format(year, sem['value'], barrioUbicacion)

                queryIndicadorSeleccion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE dia = {1} and " \
                                          "barrioid = {2} and " \
                                          "(fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                                          .format(year, sem['value'], barrioSeleccion)

                if 'user' in locals():
                    queryIndicadorPerfil = "SELECT SUM(t.cantidad) as count FROM (" \
                                           "SELECT * FROM opx.contextualizaciones " \
                                           "WHERE dia = {1} " \
                                           "and barrioid = {2}" \
                                           "and generoid = '{3}' " \
                                           "and nivelid = '{4}' " \
                                           "and edad = {5} " \
                                           "and (fecha_hecho between '{0}-01-01' and '{0}-12-31')) t" \
                                           .format(year, sem['value'], user.barrioid, user.generoid, user.nivel_educativo_id, edadUsuario)

                with connection.cursor() as cursor:

                    #Indicador Ciudad
                    cursor.execute(queryIndicadorCiudad)
                    indicadorCiudad = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesCiudad.append(indicadorCiudad)

                    #Indicador Ubicación
                    cursor.execute(queryIndicadorUbicacion)
                    indicadorUbicacion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesUbicacion.append(indicadorUbicacion)

                    #Indicador Selección
                    cursor.execute(queryIndicadorSeleccion)
                    indicadorSeleccion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesSeleccion.append(indicadorSeleccion)

                    if 'user' in locals():
                        #Indicador Perfil
                        cursor.execute(queryIndicadorPerfil)
                        indicadorPerfil = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                        conflictividadesPerfil.append(indicadorPerfil)


            data = {
                'labels': [d['label'] for d in semana],
                'datasets': [
                    {
                        'label': 'ciudad',
                        'fill': False,
                        'borderColor': 'orange',
                        'data': conflictividadesCiudad
                    },
                    {
                        'label': 'Ubicación',
                        'fill': False,
                        'borderColor': 'blue',
                        'data': conflictividadesUbicacion
                    },
                    {
                        'indicador': 'Selección',
                        'fill': False,
                        'borderColor': 'green',
                        'data': conflictividadesSeleccion
                    }
                ]
            }

            if 'user' in locals():
                data['datasets'].append({
                    'label': 'Perfil',
                    'fill': False,
                    'borderColor': 'red',
                    'data': conflictividadesPerfil
                })

            response = {
                'code': 200,
                'data': data,
                'status': 'success'
            }

        else:
            response = {
                'code': 400,
                'status': 'error'
            }

    except(IndexError):

        response = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:

        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Indicadores de conflictividades por dia
# @param request Instancia HttpRequest
# @return cadena JSON
#
def dia(request):

    try:

        barrioUbicacion = request.GET.get('barrioUbicacion')
        barrioSeleccion = request.GET.get('barrioSeleccion')
        year = request.GET.get('year')

        if request.META['HTTP_AUTHORIZATION'] != 'null':
            # Decodificando el access token
            tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                        settings.SIMPLE_JWT['VERIFYING_KEY'])
            tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

            # consultando el usuario
            user = User.objects.get(pk=tokenDecoded['user_id'])
            edadUsuario = calculoEdad(user.fecha_nacimiento)

        if barrioUbicacion is not None and barrioSeleccion is not None and year is not None:

            conflictividadesCiudad = []
            conflictividadesUbicacion = []
            conflictividadesSeleccion = []
            conflictividadesPerfil = []

            diasSemana = {
                'Sunday': 1,
                'Monday': 2,
                'Tuesday': 3,
                'Wednesday': 4,
                'Thursday': 5,
                'Friday': 6,
                'Saturday': 7
            }
            diaSemana = diasSemana.get(date.today().strftime("%A"))
            hora = 0
            horas = []

            while hora <= 23:

                horas.append(str(hora) + 'h')

                if hora < 10:
                    horaInicio = "0{}:00:00".format(str(hora))
                    horaFin = "0{}:59:59".format(str(hora))

                else:
                    horaInicio = "{}:00:00".format(str(hora))
                    horaFin = "{}:59:59".format(str(hora))

                queryIndicadorCiudad = "SELECT SUM(t.cantidad) as count FROM (" \
                                       "SELECT * FROM opx.contextualizaciones " \
                                       "WHERE dia = {1} and " \
                                       "(fecha_hecho between '{0}-01-01' and '{0}-12-31') and" \
                                       "(hora_hecho between '{2}' and '{3}')) t" \
                                       .format(year, diaSemana, horaInicio, horaFin)


                queryIndicadorUbicacion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE dia = {1} and " \
                                          "barrioid = {4} and " \
                                          "(fecha_hecho between '{0}-01-01' and '{0}-12-31') and" \
                                          "(hora_hecho between '{2}' and '{3}')) t" \
                                          .format(year, diaSemana, horaInicio, horaFin, barrioUbicacion)

                queryIndicadorSeleccion = "SELECT SUM(t.cantidad) as count FROM (" \
                                          "SELECT * FROM opx.contextualizaciones " \
                                          "WHERE dia = {1} and " \
                                          "barrioid = {4} and " \
                                          "(fecha_hecho between '{0}-01-01' and '{0}-12-31') and" \
                                          "(hora_hecho between '{2}' and '{3}')) t" \
                                          .format(year, diaSemana, horaInicio, horaFin, barrioSeleccion)

                if 'user' in locals():
                    queryIndicadorPerfil = "SELECT SUM(t.cantidad) as count FROM (" \
                                           "SELECT * FROM opx.contextualizaciones " \
                                           "WHERE dia = {1} " \
                                           "and barrioid = {4}" \
                                           "and generoid = '{5}' " \
                                           "and nivelid = '{6}' " \
                                           "and edad = {7} " \
                                           "and (fecha_hecho between '{0}-01-01' and '{0}-12-31') " \
                                           "and (hora_hecho between '{2}' and '{3}')) t" \
                                           .format(year, diaSemana, horaInicio, horaFin, user.barrioid, user.generoid, user.nivel_educativo_id, edadUsuario)

                with connection.cursor() as cursor:

                    # Indicador Ciudad
                    cursor.execute(queryIndicadorCiudad)
                    indicadorCiudad = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesCiudad.append(indicadorCiudad)

                    # Indicador Ubicación
                    cursor.execute(queryIndicadorUbicacion)
                    indicadorUbicacion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesUbicacion.append(indicadorUbicacion)

                    # Indicador Selección
                    cursor.execute(queryIndicadorSeleccion)
                    indicadorSeleccion = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                    conflictividadesSeleccion.append(indicadorSeleccion)

                    if 'user' in locals():
                        # Indicador Perfil
                        cursor.execute(queryIndicadorPerfil)
                        indicadorPerfil = verificacionExistenciaConflictividades(dictfetchall(cursor)[0]['count'])

                        conflictividadesPerfil.append(indicadorPerfil)

                hora += 1

            data = {
                'labels': horas,
                'datasets': [
                    {
                        'label': 'ciudad',
                        'fill': False,
                        'borderColor': 'orange',
                        'data': conflictividadesCiudad
                    },
                    {
                        'label': 'Ubicación',
                        'fill': False,
                        'borderColor': 'blue',
                        'data': conflictividadesUbicacion
                    },
                    {
                        'label': 'Selección',
                        'fill': False,
                        'borderColor': 'green',
                        'data': conflictividadesSeleccion
                    }
                ]
            }

            if 'user' in locals():
                data['datasets'].append({
                    'label': 'Perfil',
                    'fill': False,
                    'borderColor': 'red',
                    'data': conflictividadesPerfil
                })

            response = {
                'code': 200,
                'data': data,
                'status': 'success'
            }

        else:
            response = {
                'code': 400,
                'status': 'error'
            }

    except(IndexError):

        response = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:

        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Calculo de edad en base a una fecha de nacimiento
# @param born fecha de nacimiento del usuario
# @return numero entero con la edad del usuario
#
def calculoEdad(born):

    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

##
# @brief Cantidad de dias del mes o del año dependiendo de si es año bisiesto o no
# @param ano Año de referencia
# @param anio parametro opcional para activar verificacion del año
# @param mes parametro opcional para activar verificación del mes
# @return numero entero correspondiente a la cantidad de dias
#
def bisiesto(ano, anio=True, mes=False):

    if ano % 4 == 0  and  (ano % 100 != 0  or  ano % 400 == 0):
        if(anio):
            data = 366
        if(mes):
            data = 29
    else:
        if(anio):
            data = 365
        if(mes):
            data = 28

    return data

##
# @brief filtro final para proveer la cantidad de conflictividades
# @param cantidad resultado de la consulta asociado a la cantidad de conflictividades
# @return numero entero correspondiente a la cantidad de conflictividades
#
def verificacionExistenciaConflictividades(cantidad):

    if cantidad is None:
        response = 0
    else:
        response = cantidad

    return response