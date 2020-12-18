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

# from rest_framework.response import Response
# from rest_framework.status import (
#     HTTP_400_BAD_REQUEST,
#     HTTP_404_NOT_FOUND,
#     HTTP_200_OK
# )

# ================================ Login ================================

##
# Vista de Autenticación Dashboard
# @param request Instancia HttpRequest
# @return Plantilla Html
#
def loginView(request):

    return render(request, "auth/login.html")

##
# @brief Recurso de Autenticación de Usuarios
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):

    try:

        username = request.POST.get("username")
        password = request.POST.get("password")

        if username is None or password is None:

            data = {
               'status': 'error',
               'message': 'Por favor especifique usuario y contraseña',
               'code': 400
            }

        else:

            user = models.Usuario.objects.get(useremail__exact = username)

            #.filter(password__exact = password)
            #user = authenticate(email=username, password=password)

            # Si el correo electrónico existe
            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )
            passwordVerification = pwd_context.verify(password, user.password)

            if(passwordVerification):

                # Generación de tokens
                refresh = RefreshToken.for_user(user)

                # Almacenando los permisos del usuario en la sesión
                request.session['permisos'] = []

                permisos = models.FuncionRol.objects.filter(rolid__exact = user.rolid);

                for i in permisos:
                    request.session['permisos'].append(str(i.accionid))

                # Consultando el nombre del rol del usuario autenticado
                rol = models.Rol.objects.get(pk = user.rolid)

                data = {
                    'token': str(refresh.access_token),
                    'user': {
                        'userid':       user.userid,
                        'userfullname': user.userfullname,
                        'useremail':    user.useremail,
                        'rol':          rol.rolname,
                        'puntaje':      user.puntaje
                    },
                    'code': 200
                }

                # Puntaje esperado para llegar a rol proximo
                # Voluntario
                if str(rol.rolid) == '0be58d4e-6735-481a-8740-739a73c3be86':
                    data['user']['promocion'] = {
                        'rol': "Validador",
                        'puntaje': int(settings['umbral-validador'])
                    }

                # Proyectista
                elif str(rol.rolid) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
                    data['user']['promocion'] = {
                        'rol': "Proyectista",
                        'puntaje': int(settings['umbral-proyectista'])
                    }

            else:

                data = {
                    'status': 'error',
                    'message': 'Usuario y/o contraseña incorrecta',
                    'code': 404
                }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'message': 'Usuario y/o contraseña incorrecta',
            'code': 404
        }

    return JsonResponse(data, status = data['code'])

# ======================= usuarios ================================= 

##
# @brief Recurso de listado de usuarios
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoUsuarios(request):

    #users = models.Usuario.objects.all().values()
    # json_res = serializers.serialize('python', users)

    with connection.cursor() as cursor:
        query = "SELECT userid, userfullname, useremail, userestado, v1.usuarios.rolid, fecha_nacimiento, \
                barrioid, generoid, nivel_educativo_id, telefono, v1.roles.rolname, latitud, longitud, \
                horaubicacion, fecha_creacion, empleado \
                FROM v1.usuarios \
                INNER JOIN v1.roles ON v1.roles.rolid = v1.usuarios.rolid"

        cursor.execute(query)
        users = dictfetchall(cursor)

        return JsonResponse(users, safe=False)

##
# @brief Recurso que provee el detalle de un usuario registrado
# @param userid identificación del usuario
# @return Cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def detalleUsuario(request, userid):

    try:
        #usuario = models.Usuario.objects.get(pk=userid)
        usuario = {}

        with connection.cursor() as cursor:
            query = "SELECT u.*, r.rolname from v1.usuarios u \
                    INNER JOIN v1.roles r ON r.rolid = u.rolid " \
                    "WHERE u.userid = '{}'".format(userid)
            cursor.execute(query)
            queryResult = dictfetchall(cursor)

        if(len(queryResult) > 0):

            usuario = queryResult[0]

            # Puntaje esperado para llegar a rol proximo
            # Voluntario
            if str(usuario['rolid']) == '0be58d4e-6735-481a-8740-739a73c3be86':
                usuario['promocion'] = {
                    'rol': "Validador",
                    'puntaje': int(settings['umbral-validador'])
                }

            # Proyectista
            elif str(usuario['rolid']) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
                usuario['promocion'] = {
                    'rol': "Proyectista",
                    'puntaje': int(settings['umbral-proyectista'])
                }

            # Remover la información que no se desea mostrar
            del usuario['password']
            del usuario['usertoken']

            data = {
                'code': 200,
                'usuario': usuario,
                'status': 'success'
            }

        else:
            raise ObjectDoesNotExist("")

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:

        data = {
            'code': 400,
            'status': 'error'
        }

    except DataError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status=data['code'])

##
# @brief Recurso de almacenamiento de usuarios
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def almacenarUsuario(request):

    useremail = request.POST.get('useremail')
    usertoken = request.POST.get('usertoken')
    userfullname = request.POST.get('userfullname')
    password = request.POST.get('password')
    rolid = request.POST.get('rolid')
    userleveltype = 1
    userestado = 1
    fechaNacimiento = request.POST.get('fecha_nacimiento')
    genero = request.POST.get('generoid')
    barrio = request.POST.get('barrioid')
    nivelEducativo = request.POST.get('nivel_educativo_id')
    telefono = request.POST.get('telefono')
    fechaCreacion = datetime.today()
    empleado = request.POST.get('empleado')

    usuario = models.Usuario(useremail = useremail, usertoken = usertoken, userfullname = userfullname,
                             password = password, rolid = rolid, userleveltype = userleveltype,
                             userestado = userestado, fecha_nacimiento = fechaNacimiento, generoid = genero,
                             barrioid = barrio, nivel_educativo_id = nivelEducativo, telefono = telefono,
                             fecha_creacion=fechaCreacion)

    try:
        # Asignación de estado "empleado" a usuario en caso tal sea enviado
        if empleado is not None:
            if empleado == "true":
                usuario.empleado = 1
            else:
                usuario.empleado = 0

        # Validación de campos
        usuario.full_clean()

        # Contexto Passlib
        pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=30000
        )
        usuario.password = pwd_context.encrypt(usuario.password)

        usuario.save()

        data = {
            'code': 201,
            'usuario': serializers.serialize('python', [usuario])[0],
            'status': 'success'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'errors': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status=data['code'])

##
# @brief Recurso de eliminación de usuarios
# @param request Instancia HttpRequest
# @param userid Identificación de usuario autenticado
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarUsuario(request, userid):

    try:
        usuario = models.Usuario.objects.get(userid = userid)

        usuario.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de Actualización de usuarios
# @param request Instancia HttpRequest
# @param userid Identificación de usuario autenticado
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarUsuario(request, userid):
    
    try:

        # Obteniendo datos respecto a la ubicacion del usuario
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')

        # Asignando la nueva información al usuario
        usuario = models.Usuario.objects.get(pk = userid)

        usuario.useremail = request.POST.get('useremail')
        usuario.rolid = request.POST.get('rolid')
        usuario.userfullname = request.POST.get('userfullname')
        usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        usuario.generoid = request.POST.get('generoid')
        usuario.barrioid = request.POST.get('barrioid')
        usuario.nivel_educativo_id = request.POST.get('nivel_educativo_id')
        usuario.telefono = request.POST.get('telefono')

        #Asignando la información de ubicacion al usuario en caso de ser enviada
        if latitud is not None and longitud is not None:
            usuario.latitud = latitud
            usuario.longitud = longitud
            usuario.horaubicacion = datetime.today()

        #Asignando la nueva contraseña en caso de ser enviada
        if request.POST.get('password') is not None and len(request.POST.get('password')) > 0:

            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )
            usuario.password = pwd_context.encrypt(request.POST.get('password'))

        # Asignando el estado "empleado" del usuario en tal caso sea enviado
        if request.POST.get('empleado') is not None:
            if request.POST.get('empleado') == "true":
                usuario.empleado = 1
            else:
                usuario.empleado = 0

        usuario.full_clean()

        usuario.save()

        data = {
            'code': 200,
            'usuario': serializers.serialize('python', [usuario])[0],
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

    except IntegrityError as e:

        data = {
            'code': 500,
            'errors': str(e),
            'status': 'error'
        }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief plantilla de listado de usuarios
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoUsuariosView(request):

    return render(request, "usuarios/listado.html")

# ======================== Contextos ===============================

##
# @brief Recurso de listado de contextos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoContextos(request):

    contextos = models.Contexto.objects.all().values()

    return JsonResponse(list(contextos), safe = False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoContextosProyecto(request, proyid):

    try:
        models.Proyecto.objects.get(pk=proyid)

        # Listado de IDS de contexto
        contextos = []
        contextosID = models \
                    .ContextoProyecto \
                    .objects \
                    .filter(proyid=proyid)

        # Inserción de IDs en lista para consulta posterior
        for contexto in contextosID:
            contextos.append(str(contexto.contextoid))

        # Consulta de contextos
        contextos = models.Contexto.objects.filter(pk__in=contextos).values()

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

    descripcion = request.POST.get('descripcion');

    contexto = models.Contexto(descripcion=descripcion)

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

    try:
        contexto = models.Contexto.objects.get(pk = contextoid)

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

    descripcion = request.POST.get('descripcion')

    try:
        contexto = models.Contexto.objects.get(pk = contextoid)

        contexto.descripcion = descripcion

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

            print(coordenadas)
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

    contextos = models.Contexto.objects.all()

    if contextos:

        for c in contextos:

            datosContexto = models.DatosContexto.objects.filter(contextoid__exact = c.contextoid)

            if datosContexto:

                contextosList.append({
                    'contextoid': c.contextoid,
                    'contexto': c.descripcion,
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

    datosContexto = models.DatosContexto.objects.filter(contextoid__exact = contextoid).values()

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
                    'descripcion': data[1],
                    'valor': data[2],
                    'metrica': data[3],
                    'geojson': geopandaGeojson(data[4]),
                    'fecha': fecha,
                    'hora': hora
                   })

                try:
                    with transaction.atomic():

                      contextoid = request.POST.get('contextoid')

                      for dt in datosContexto:
                         datosContexto = models.DatosContexto(hdxtag=dt['hdxtag'], datavalor=dt['valor'], datatipe= dt['metrica'], contextoid=contextoid, descripcion = dt['descripcion'], geojson = dt['geojson'], fecha=dt['fecha'], hora=dt['hora'])
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
        datoContexto = models.DatosContexto.objects.get(pk = dataid)

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
        datoContexto = models.DatosContexto.objects.get(pk=dataid)

        datoContexto.hdxtag = request.POST.get('hdxtag')
        datoContexto.descripcion = request.POST.get('descripcion')
        datoContexto.datavalor = request.POST.get('datavalor')
        datoContexto.datatipe = request.POST.get('datatipe')

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
        contexto = models.Contexto.objects.get(pk = contextoid)

        return render(request, "contextos/datos-contexto.html", {'contexto': contexto})

    except ObjectDoesNotExist:
        code = 404

    except ValidationError:
        code = 400

    return HttpResponse("", status = code)

# ======================== Decisiones =============================

##
# @brief Recurso de listado de decisiones
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDecisiones(request):

    # decisiones = models.Decision.objects.all().values()
    #
    # return JsonResponse(list(decisiones), safe = False)

    with connection.cursor() as cursor:
        cursor.execute("select v1.decisiones.desiid, v1.decisiones.desidescripcion, v1.usuarios.userid, v1.usuarios.userfullname from v1.decisiones inner join v1.usuarios on v1.decisiones.userid = v1.usuarios.userid")

        columns = dictfetchall(cursor)

        return JsonResponse(columns, safe = False)

##
# @brief Recurso de almacenamiento de decisiones
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenarDecision(request):

    desidescripcion = request.POST.get('desidescripcion')
    userid = usuarioAutenticado(request).userid

    decision = models.Decision(desidescripcion = desidescripcion, userid = userid)

    try:
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

    try:
        decision = models.Decision.objects.get(pk = desiid)

        decision.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

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
        decision = models.Decision.objects.get(pk=desiid)

        decision.desidescripcion = request.POST.get('desidescripcion')
        # decision.userid = request.POST.get('userid')

        decision.full_clean()

        decision.save()

        return JsonResponse(serializers.serialize('python', [decision]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

##
# @brief Plantilla de decisiones
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoDecisionesView(request):

    return render(request, "decisiones/listado.html")


# ========================== Decisiones Proyecto ==================

##
# @brief Recurso de listado de decisiones Proyecto
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDecisionesProyecto(request):

    decisionesProyecto = models.DecisionProyecto.objects.all().values()

    return JsonResponse(list(decisionesProyecto), safe = False)

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listDecisionesProyecto(request, proyid):

    try:
        # Verificación de existencia de proyecto
        models.Proyecto.objects.get(pk=proyid)

        # Listado de IDS de decisiones
        decisiones = []
        decisionesIDS = models \
                        .DecisionProyecto \
                        .objects \
                        .filter(proyid=proyid)

        for decision in decisionesIDS:
            decisiones.append(decision.desiid)

        # Consulta
        decisiones = models \
                    .Decision \
                    .objects \
                    .filter(pk__in=decisiones) \
                    .values()

        response = {
            'code':         200,
            'decisiones':   list(decisiones),
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
# @brief Recurso de eliminación de decisiones Proyecto
# @param request Instancia HttpRequest
# @param desproid Identificación de Decision Proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarDecisionProyecto(request, desproid):

    try:
        decisionProyecto = models.DecisionProyecto.objects.get(pk = desproid)

        decisionProyecto.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de actualización de decisiones Proyecto
# @param request Instancia HttpRequest
# @param desproid Identificación de Decisión Proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarDecisionProyecto(request, desproid):
    try:
        decisionProyecto = models.DecisionProyecto.objects.get(pk=desproid)

        decisionProyecto.proyid = request.POST.get('proyid')
        decisionProyecto.desiid = request.POST.get('desiid')

        decisionProyecto.full_clean()

        decisionProyecto.save()

        return JsonResponse(serializers.serialize('python', [decisionProyecto]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

# ========================= Funciones Rol =========================

##
# @brief Recurso de listado de Funciones del Sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoAcciones(request):

    acciones = models.Accion.objects.all().values()

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
        cursor.execute("select v1.funciones_rol.funcrolid, v1.acciones.nombre from v1.funciones_rol inner join v1.acciones on v1.funciones_rol.accionid = v1.acciones.accionid where v1.funciones_rol.rolid = %s", [rolid])

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
    funcRolEstado = 1
    funcRolPermiso = 1

    funcionRol = models.FuncionRol(rolid = rolID, accionid = accionID, funcrolestado = funcRolEstado, funcrolpermiso = funcRolPermiso)

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

    try:
        funcionRol = models.FuncionRol.objects.get(pk = funcrolid)

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
        funcionRol = models.FuncionRol.objects.get(pk=funcrolid)

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

        instrumentos =  models.Instrumento.objects.all().values()

    else:

        instrumentos = models.Instrumento.objects.filter(instrtipo__exact = instrtipo).values()

    response = JsonResponse(list(instrumentos), safe = False)

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

    if(instrTipo is None):
        return JsonResponse({'status': 'error'}, status = 400)

    if instrTipo == "1":
        instrIdExterno = request.POST.get('instridexterno')

    elif instrTipo == "2":
        instrIdExterno = almacenarProyectoTM(instrNombre, json.loads(areaInteres))

        if not instrIdExterno:
            instrIdExterno = "12345"

    else:
        instrIdExterno = "12345"

    instrumento = models.Instrumento(instridexterno = instrIdExterno, instrtipo = instrTipo, instrnombre = instrNombre, instrdescripcion = instrDescripcion, geojson = areaInteres)

    try:
        instrumento.full_clean()

        if instrumento.instridexterno == '12345':

            return JsonResponse({}, safe = False, status = 500)

        else:

            instrumento.save()
            data = serializers.serialize('python', [instrumento])
            return JsonResponse(data, safe = False, status = 201)

    except ValidationError as e:
        return JsonResponse(dict(e), safe = True, status = 400)

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
        instrumento = models.Instrumento.objects.get(pk = instrid)

        instrumento.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

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
        instrumento = models.Instrumento.objects.get(pk=instrid)

        #instrumento.instridexterno = request.POST.get('instridexterno')
        #instrumento.instrtipo = request.POST.get('instrtipo')
        instrumento.instrnombre = request.POST.get('instrnombre')
        instrumento.instrdescripcion = request.POST.get('instrdescripcion')

        instrumento.full_clean()

        instrumento.save()

        return JsonResponse(serializers.serialize('python', [instrumento]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:

        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

# ============================ Encuestas ==========================
##
# @brief Recurso de almacenamiento de encuestas
# @param instrumento Instancia modelo Instrumento
# @param informacion dataset de encuestas a almacenar
# @param userid Identificación del usuario
# @param tareid Identificación de la tarea
# @return Diccionario
#
def almacenarEncuestas(instrumento, informacion, userid, tareid):

    try:
        with transaction.atomic():
            for info in informacion:
                
                try:
                    models.Encuesta.objects.get(koboid__exact=info['_uuid'])
                    
                except ObjectDoesNotExist:
                
                    encuesta = models.Encuesta(instrid=instrumento.instrid, koboid = info['_uuid'], contenido=json.dumps(info), userid=userid, tareid=tareid)
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
        encuesta = models.Encuesta.objects.get(pk=encuestaid)

        encuesta.observacion = request.POST.get('observacion')
        encuesta.estado = request.POST.get('estado')

        encuesta.full_clean()
        encuesta.save()

        response = {
            'code': 200,
            #'encuesta': model_to_dict(encuesta),
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
# @brief Recurso para obtener información de instrumentos
# @param request Instancia HttpRequest
# @param id Indentificación del instrumento
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def informacionInstrumento(request, id):

    try:
        tarea = models.Tarea.objects.get(pk=id)
        instrumento = models.Instrumento.objects.get(pk = tarea.instrid)

        if instrumento.instrtipo == 1:

            informacion = informacionFormularioKoboToolbox(instrumento.instridexterno)

            if(isinstance(informacion, dict)):

                #almacenarEncuestas(instrumento, informacion['info'])
                encuestasDB = models.Encuesta.objects.filter(tareid__exact=tarea.tareid)
                encuestas = []

                for e in encuestasDB:
                    contenido = json.loads(e.contenido)
                    contenido['encuestaid'] = e.encuestaid
                    contenido['estado'] = e.estado
                    contenido['observacion'] = e.observacion

                    encuestas.append(contenido)

                data = {
                    'status': 'success',
                    'code': 200,
                    'info': {
                        'campos': informacion['campos'],
                        'info': encuestas,
                        'tipoInstrumento': instrumento.instrtipo
                    },
                    'instrumento': model_to_dict(instrumento)
                }

            else:

                data = {
                    'status': 'error',
                    'code': 500
                }

        elif instrumento.instrtipo == 2:

            informacion = informacionProyectoTM(instrumento.instridexterno)
            informacionMapeo = detalleCartografia(str(tarea.tareid))

            if(informacionMapeo['code'] == 200):
                geojson = informacionMapeo['geojson']
            else:
                geojson = "{}"

            if (isinstance(informacion, dict)):

                informacion['tipoInstrumento'] = instrumento.instrtipo

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

    return JsonResponse(data, status = data['code'])

##
# @brief Plantilla de Instrumentos
# @param request Instancia HttpRequest
# @return Plantilla HTML
#
def listadoInstrumentosView(request):

    return render(request, "instrumentos/listado.html")

##
# @brief Plantilla para información de Instrumento
# @param request Instancia HttpRequest
# @param id Identificación del instrumento
# @return Plantilla HTML
#
def informacionInstrumentoView(request, id):

    try:
        instrumento = models.Instrumento.objects.get(pk = id)

        return render(request, "instrumentos/informacion.html", {'instrumento': instrumento})

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", 400)

##
# @brief Plantilla de creación de Encuesta
# @param request Instancia HttpRequest
# @return Plantilla HTML
#
def creacionEncuestaView(request):

    return render(request, "instrumentos/creacion-encuesta.html")

# ============================ Roles =============================

##
# @brief Recurso de Listao de Roles
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoRoles(request):

    roles = models.Rol.objects.filter(rolestado__exact=1).values()

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

    rol = models.Rol(rolname = rolName, roldescripcion = rolDescripcion, rolestado = rolEstado)

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
        rol = models.Rol.objects.get(pk = rolid)

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
        rol = models.Rol.objects.get(pk=rolid)

        rol.rolname = request.POST.get('rolname')
        rol.roldescripcion = request.POST.get('roldescripcion')        
        # rol.rolestado = request.POST.get('rolestado')

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
        rol = models.Rol.objects.get(pk = rolid)

        return render(request, "roles/permisos.html", {'rol': rol})

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", status = 400)

# ================= Kobo Toolbox ========================

##
# @brief Obtenención de encuestas de un formulario KoboToolbox
# @param id Identificación del Formulario KoboToolbox
# @return Diccionario
#
def informacionFormularioKoboToolbox(id):

    headers = {'Authorization': settings['kobo-token']}

    client = http.client.HTTPConnection(settings['kobo-kpi'], int(settings['kobo-puerto']), timeout = int(settings['timeout-request']))

    client.request('GET', '/assets/' + id + '/submissions/', '{}', headers)

    response = client.getresponse()

    if(response.status == 200):

        info = json.loads(response.read())

        # ============== Obteniendo campos del formulario====================

        detalleFormulario = detalleFormularioKoboToolbox(id)

        if (detalleFormulario):

            camposFormulario = detalleFormulario['content']['survey']

            data = {
                'campos': camposFormulario,
                'info': info
            }

        else:
            data = False

    else:
        data = False

    client.close()

    return data

##
# @brief Obtención de información de detalle de un formulario de KoboToolbox
# @param id Identificación del Formulario KoboToolbox
# @return Diccionario
#
def detalleFormularioKoboToolbox(id):

    headers = {'Authorization': settings['kobo-token']}

    client = http.client.HTTPConnection(settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))
    client.request('GET', '/assets/' + str(id) + '/?format=json', '', headers)
    response = client.getresponse()

    if (response.status == 200):

        data = json.loads(response.read())

    else:
        data = False

    return data

##
# @brief Obtención de enlace de diligenciamiento de un formulario de KoboToolbox
# @param id tareid Identificación de la tarea Tipo Encuesta
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def enlaceFormularioKoboToolbox(request, tareid):

    headers = {'Authorization': settings['kobo-token']}

    try:
        tarea = models.Tarea.objects.get(pk = tareid)

        instrumento = models.Instrumento.objects.get(pk = tarea.instrid)

        if instrumento.instrtipo == 1:

            informacion = informacionFormularioKoboToolbox(instrumento.instridexterno)

            if (isinstance(informacion, dict)):

                user = usuarioAutenticado(request)
                almacenarEncuestas(instrumento, informacion['info'], user.userid, tarea.tareid)

            detalleFormulario = detalleFormularioKoboToolbox(instrumento.instridexterno)

            if detalleFormulario:

                if(detalleFormulario['deployment__active']):

                    if detalleFormulario['deployment__submission_count'] < tarea.tarerestriccant:

                        enlace = detalleFormulario['deployment__links']['offline_url']

                        data = {
                            'code': 200,
                            'enlace': enlace,
                            'status': 'success'
                        }

                    else:

                        # La tarea ya esta completada y se marca como terminada si esta en progreso
                        if tarea.tareestado == 0:
                            tarea.tareestado = 1
                            tarea.save()

                        data = {
                            'code': 403,
                            'message': 'Tarea completada',
                            'status': 'error'
                        }

                else:

                    data = {
                        'code': 400,
                        'message': 'El formulario no está implementado',
                        'status': 'error'
                    }

            else:

                data = {
                    'code': 500,
                    'status': 'error'
                }

        else:

            data = {
                'code': 400,
                'message': 'El instrumento no es de tipo encuesta',
                'status': 'error'
            }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Implementación/Despliegue de un formulario de KoboToolbox
# @param id Identificación del Formulario KoboToolbox
# @return cadena JSON
#
@csrf_exempt
def implementarFormularioKoboToolbox(request, id):

    try:

        instrumento = models.Instrumento.objects.get(pk = id)

        headers = {
            'Authorization': settings['kobo-token'],
            'Content-Type': 'application/json'
        }

        payload = {'active': True}

        client = http.client.HTTPConnection(settings['kobo-kpi'], int(settings['kobo-puerto']), timeout = int(settings['timeout-request']))

        client.request('POST', '/assets/' + instrumento.instridexterno + '/deployment/', json.dumps(payload), headers)

        response = client.getresponse()

        if response.status != 200:

            data = {
                'status': 'error',
                'code': 500
            }

        else:

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
            'code': 400
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Listado de formularios de KoboToolbox
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoFormulariosKoboToolbox(request):

    try:

        headers = {
            'Authorization': settings['kobo-token'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }

        client = http.client.HTTPConnection(settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))
        client.request('GET', '/assets/?format=json', '', headers)
        response = client.getresponse()

        if(response.status == 200):

            formulariosKoboToolbox = json.loads(response.read())['results']

            data = {
                'code': 200,
                'formularios': formulariosKoboToolbox,
                'status': 'success'
            }

        else:
            print("Oops!", sys.exc_info()[0], "occurred.")
            data = {
                'code': 500,
                'status': 'error'
            }

    except:
        print("Oops!", sys.exc_info()[0], "occurred.")
        data = {
            'code': 500,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'], safe = False)

##
# @brief Verificación de Implementación/Despliegue de un formulario de KoboToolbox
# @param request Instancia HttpRequest
# @param id Identificación del Formulario KoboToolbox
# @return cadena JSON
#
def verificarImplementaciónFormulario(request, id):

    try:
        instrumento = models.Instrumento.objects.get(pk = id)

        headers = {
            'Authorization': settings['kobo-token'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }

        client = http.client.HTTPConnection(settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))
        client.request('GET', '/assets/?format=json', '', headers)
        response = client.getresponse()

        if(response.status == 200):

            formulariosKoboToolbox = json.loads(response.read())['results']

            for i in formulariosKoboToolbox:

                if(i['uid'] == instrumento.instridexterno):

                    if(i['has_deployment']):

                        data = {
                            'code': 200,
                            'status': 'success',
                            'implementacion': True
                        }

                    else:

                        data = {
                            'code': 200,
                            'status': 'success',
                            'implementacion': False
                        }

                    break

                else:

                    data = {
                        'code': 404,
                        'status': 'error'
                    }

        else:

            data = {
                'code': 500,
                'status': 'error'
            }

    except ObjectDoesNotExist:

        data = {
            'status': 'success',
            'code': 404
        }

    except ValidationError:

        data = {
            'status': 'error',
            'code': 400
        }

    return JsonResponse(data, status = data['code'])

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

    client = http.client.HTTPConnection(settings['tm'], int(settings['tm-puerto']), timeout = int(settings['timeout-request']))
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

    client = http.client.HTTPConnection(settings['tm'], int(settings['tm-puerto']), timeout = int(settings['timeout-request']))
    client.request('GET', '/api/v1/project/' + id, {}, headers)
    response = client.getresponse()

    if (response.status != 200):

        data =  False

    else:

        data =  json.loads(response.read())

    return data

# ==================== Perfil ================

##
# @brief Plantilla de Perfil de Usuario
# @param request instancia HttpRequest
# @return plantilla HTML
#
def perfilView(request):
    return render(request, "perfil/gestion.html")
