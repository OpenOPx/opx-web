from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext
import shapely.geometry
import geopandas

from myapp import models

from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import (connection, transaction)
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp.view.utilidades import dictfetchall

# from rest_framework.response import Response
# from rest_framework.status import (
#     HTTP_400_BAD_REQUEST,
#     HTTP_404_NOT_FOUND,
#     HTTP_200_OK
# )

# ================================ Login ================================

def loginView(request):

    return render(request, "auth/login.html")

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
                        'userid': user.userid,
                        'userfullname': user.userfullname,
                        'useremail': user.useremail,
                        'rol': rol.rolname
                    },
                    'code': 200
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

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoUsuarios(request):

    #users = models.Usuario.objects.all().values()
    # json_res = serializers.serialize('python', users)

    with connection.cursor() as cursor:
        cursor.execute("SELECT userid, userfullname, useremail, userestado, v1.usuarios.rolid, fecha_nacimiento, barrioid, generoid, nivel_educativo_id, telefono, v1.roles.rolname FROM v1.usuarios INNER JOIN v1.roles ON v1.roles.rolid = v1.usuarios.rolid")
        columns = dictfetchall(cursor)

        return JsonResponse(columns, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def detalleUsuario(request, userid):

    try:
        usuario = models.Usuario.objects.get(pk=userid)

        data = {
            'code': 200,
            'usuario': model_to_dict(usuario),
            'status': 'success'
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

    return JsonResponse(data, status=data['code'])


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

    usuario = models.Usuario(useremail = useremail, usertoken = usertoken, userfullname = userfullname, password = password, rolid = rolid, userleveltype = userleveltype, userestado = userestado, fecha_nacimiento = fechaNacimiento, generoid = genero, barrioid = barrio, nivel_educativo_id = nivelEducativo, telefono = telefono)

    try:
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

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarUsuario(request, userid):
    
    try:
        usuario = models.Usuario.objects.get(pk = userid)

        usuario.useremail = request.POST.get('useremail')
        usuario.rolid = request.POST.get('rolid')
        usuario.userfullname = request.POST.get('userfullname')
        usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        usuario.generoid = request.POST.get('generoid')
        usuario.barrioid = request.POST.get('barrioid')
        usuario.nivel_educativo_id = request.POST.get('nivel_educativo_id')
        usuario.telefono = request.POST.get('telefono')

        if request.POST.get('password') is not None and len(request.POST.get('password')) > 0:

            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )
            usuario.password = pwd_context.encrypt(request.POST.get('password'))

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

def listadoUsuariosView(request):

    return render(request, "usuarios/listado.html")

# ======================== Contextos ===============================

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoContextos(request):

    contextos = models.Contexto.objects.all().values()

    return JsonResponse(list(contextos), safe = False)

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

def listadoContextosView(request):

    return render(request, "contextos/listado.html")

# ======================== Datos de Contexto =======================

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

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenarDecision(request):

    desidescripcion = request.POST.get('desidescripcion')
    userid = request.POST.get('userid')    

    decision = models.Decision(desidescripcion = desidescripcion, userid = userid)

    try:
        decision.full_clean()

        decision.save()
        data = serializers.serialize('python', [decision])
        return JsonResponse(data, safe = False, status = 201)

    except ValidationError as e:
        return JsonResponse(dict(e), safe = True, status = 400)

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

def listadoDecisionesView(request):

    return render(request, "decisiones/listado.html")


# ========================== Decisiones Proyecto ==================

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDecisionesProyecto(request):

    decisionesProyecto = models.DecisionProyecto.objects.all().values()

    return JsonResponse(list(decisionesProyecto), safe = False)

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

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoAcciones(request):

    acciones = models.Accion.objects.all().values()

    return JsonResponse(list(acciones), safe = False)

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoFuncionesRol(request, rolid):

    with connection.cursor() as cursor:
        cursor.execute("select v1.funciones_rol.funcrolid, v1.acciones.nombre from v1.funciones_rol inner join v1.acciones on v1.funciones_rol.accionid = v1.acciones.accionid where v1.funciones_rol.rolid = %s", [rolid])

        columns = dictfetchall(cursor)

        return JsonResponse(columns, safe = False)

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

def informacionInstrumento(request, id):

    try:
        instrumento = models.Instrumento.objects.get(pk = id)

        if instrumento.instrtipo == 1:

            informacion = informacionFormularioKoboToolbox(instrumento.instridexterno)

            if(isinstance(informacion, dict)):

                informacion['tipoInstrumento'] = instrumento.instrtipo

                data = {
                    'status': 'success',
                    'code': 200,
                    'info': informacion,
                    'instrumento': model_to_dict(instrumento)
                }

            else:

                data = {
                    'status': 'error',
                    'code': 500
                }

        elif instrumento.instrtipo == 2:

            informacion = informacionProyectoTM(instrumento.instridexterno)

            if (isinstance(informacion, dict)):

                informacion['tipoInstrumento'] = instrumento.instrtipo

                data = {
                    'status': 'success',
                    'code': 200,
                    'info': informacion,
                    'instrumento': instrumento
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

def listadoInstrumentosView(request):

    return render(request, "instrumentos/listado.html")

def informacionInstrumentoView(request, id):

    try:
        instrumento = models.Instrumento.objects.get(pk = id)

        return render(request, "instrumentos/informacion-encuesta.html", {'instrumento': instrumento})

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", 400)

def creacionEncuestaView(request):

    return render(request, "instrumentos/creacion-encuesta.html")

# ============================ Roles =============================

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoRoles(request):

    roles = models.Rol.objects.all().values()

    data = {
        'code': 200,
        'roles': list(roles),
        'status': 'success'
    }

    return JsonResponse(data, safe = False, status = data['code'])

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

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarRol(request, rolid):
    try:
        rol = models.Rol.objects.get(pk=rolid)

        rol.rolname = request.POST.get('rolname')
        rol.roldescripcion = request.POST.get('roldescripcion')        
        rol.rolestado = request.POST.get('rolestado')

        rol.full_clean()

        rol.save()

        return JsonResponse(serializers.serialize('python', [rol]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

def listadoRolesView(request):

    return render(request, "roles/listado.html")

def permisosRolView(request, rolid):

    try:
        rol = models.Rol.objects.get(pk = rolid)

        return render(request, "roles/permisos.html", {'rol': rol})

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", status = 400)

# ================= Kobo Toolbox ========================

def informacionFormularioKoboToolbox(id):

    headers = {'Authorization': 'Token 9e65dbdf164fbcee05f739d5e2d269e908760d8d'}

    client = http.client.HTTPConnection("kf.oim-opc.pre", 80, timeout = 10)

    client.request('GET', '/assets/' + id + '/submissions/', '{}', headers)

    response = client.getresponse()

    if(response.status != 200):

        data = False

    else:

        info = json.loads(response.read())

        # ============== Obteniendo campos del formulario====================

        client = http.client.HTTPConnection("kf.oim-opc.pre", 80, timeout=10)
        client.request('GET', '/assets/?format=json', '', headers)
        response = client.getresponse()

        if (response.status == 200):

            formulariosKoboToolbox = json.loads(response.read())['results']

            for i in formulariosKoboToolbox:

                if (i['uid'] == id):

                    campos = i['summary']['labels']
                    break

            data = {
                'campos': campos,
                'info': info
            }

        else:

            data = False

    client.close()

    return data

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def enlaceFormularioKoboToolbox(request, instrid):

    headers = {'Authorization': 'Token 9e65dbdf164fbcee05f739d5e2d269e908760d8d'}

    try:
        instrumento = models.Instrumento.objects.get(pk = instrid)

        if instrumento.instrtipo == 1:

            httpClient = http.client.HTTPConnection("kf.oim-opc.pre", 80, timeout = 10)
            httpClient.request("GET", '/assets/' + instrumento.instridexterno + '/?format=json', '', headers)
            response = httpClient.getresponse()

            if response.status == 200:

                informacion = json.loads(response.read())

                if(informacion['deployment__active']):

                    enlace = informacion['deployment__links']['offline_url']

                    data = {
                        'code': 200,
                        'enlace': enlace,
                        'status': 'success'
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

@csrf_exempt
def implementarFormularioKoboToolbox(request, id):

    try:

        instrumento = models.Instrumento.objects.get(pk = id)

        headers = {
            'Authorization': 'Token 9e65dbdf164fbcee05f739d5e2d269e908760d8d',
            'Content-Type': 'application/json'
        }

        payload = {'active': True}

        client = http.client.HTTPConnection("kf.oim-opc.pre", 80, timeout = 10)

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

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoFormulariosKoboToolbox(request):

    try:

        headers = {
            'Authorization': 'Token 9e65dbdf164fbcee05f739d5e2d269e908760d8d',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }

        client = http.client.HTTPConnection("kf.oim-opc.pre", 80, timeout=10)
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
            data = {
                'code': 500,
                'status': 'error'
            }

    except:

        data = {
            'code': 500,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'], safe = False)

def verificarImplementaciónFormulario(request, id):

    try:
        instrumento = models.Instrumento.objects.get(pk = id)

        headers = {
            'Authorization': 'Token 9e65dbdf164fbcee05f739d5e2d269e908760d8d',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }

        client = http.client.HTTPConnection("kf.oim-opc.pre", 80, timeout=10)
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

def almacenarProyectoTM(nombre, areaInteres):

    headers = {
        'Authorization': 'Token T1RNM09UQTJOUS5FSk5laWcuTXBGZnNpV05lVUp3MnB1bm9reGJONUZ2SEZF',
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

    client = http.client.HTTPConnection('oim-opc.pre', 30802, timeout = 10)
    client.request('PUT', '/api/v1/admin/project', json.dumps(info), headers)
    response = client.getresponse()

    if response.status == 201:
        return json.loads(response.read())['projectId']

    else:
        return False

def informacionProyectoTM(id):
    headers = {
        'Authorization': 'Token T1RNM09UQTJOUS5FSk5laWcuTXBGZnNpV05lVUp3MnB1bm9reGJONUZ2SEZF'
    }

    client = http.client.HTTPConnection('oim-opc.pre', 30802, timeout = 10)
    client.request('GET', '/api/v1/project/' + id, {}, headers)
    response = client.getresponse()

    if (response.status != 200):

        data =  False

    else:

        data =  json.loads(response.read())

    return data