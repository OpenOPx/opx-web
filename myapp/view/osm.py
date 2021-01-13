import base64
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import connection
from django.db.utils import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from myapp import models
from myapp.view.utilidades import dictfetchall, usuarioAutenticado
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from shapely.geometry import Polygon, LineString, shape
from xml.etree.ElementTree import Element, SubElement, tostring

import geopandas
import http.client
import json
# import json.decoder.jso
import xml.etree.ElementTree as ET

from opc.opc_settings import settings

#@brief url de API REST Open Street Maps
if 'osm-api-url' in settings.keys():
    osmRestApiUrl = settings['osm-api-url']

##
# @brief Función que provee las cabeceras que requiere el API REST de Open Street Maps
# @return Diccionario
#
def osmHeaders():

    #credentials = 'inge4neuromedia@gmail.com:;K7c8`EQ+82eyHKd'.encode('utf-8')
    credentials = 'develop.opx@gmail.com:12345678'.encode('utf-8')
    credentialsEncode = str(base64.b64encode(credentials), 'utf-8')

    headers = {
        'Authorization': 'Basic ' + credentialsEncode,
        'Content-Type': 'text/xml'
    }

    return headers

##
# @brief Función que agrega un nuevo changeset en Open Street Maps
# @return Respuesta de API de Open Street Maps
#
def agregarChangeset():

    try:
        #Armando XML
        root = Element('osm')

        changeset = SubElement(root, 'changeset')
        changeset.set('version', '0.6')

        tag = SubElement(changeset, 'tag')
        tag.set('k', 'comment')
        tag.set('v', 'test')

        client = http.client.HTTPSConnection(osmRestApiUrl)
        client.request('PUT', '/api/0.6/changeset/create', tostring(root), osmHeaders())

        response = client.getresponse()

        if response.status == 200:
            return str(response.read(), 'utf-8')

        else:
            raise TypeError("Error Al intentar Crear Changeset OSM: " + str(response.read(), 'utf-8'))

    except:
        raise TypeError("Error Al intentar Crear Changeset OSM " + str(response.read(), 'utf-8'))

##
# @brief Funcion que cierre Changeset en Open Street Maps
# @param changeset changeset abierto de Open Street Maps
# @return Respuesta de API de Open Street Maps
#
def cerrarChangeset(changeset):

    client = http.client.HTTPSConnection(osmRestApiUrl)
    client.request('PUT', '/api/0.6/changeset/' + changeset + '/close', None, osmHeaders())

    response = client.getresponse()

##
# @brief Recurso que agrega elemento en Open Street Maps
# @param request Instancia HttpRequest
# @param tareid Identificación de la tarea
# @return Cadena JSON
#
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def AgregarElemento(request, tareid):

    try:
        tarea = models.Task.objects.get(pk=tareid)
        #instrumento = models.Instrument.objects.get(pk = tarea.instrument.instrument_id)
        instrumento = tarea.instrument
        if instrumento.instrument_type == 2:

            data = json.loads(request.body)
            osmelement = models.OsmElement.objects.get(pk = data['osmelement'])

            if osmelement.closed_way == 1:
                coordinates = data['coordinates']
            else:
                coordinates = data['coordinates']

            nodes = []
            changeset = agregarChangeset()
            nodeCount = 0

            # Armando XML
            root = Element('osmChange')
            root.set('version', '0.6')

            create = SubElement(root, 'create')

            # Creando Nodos

            for c in coordinates:
                nodeCount -= 1
                longitud = str(c['lng'])
                latitud = str(c['lat'])

                node = SubElement(create, 'node')
                node.set('id', str(nodeCount))
                node.set('lon', longitud)
                node.set('lat', latitud)
                node.set('version', "0")
                node.set('changeset', changeset)

                nodes.append(node)

            #Creando Way
            way = SubElement(create, 'way')
            way.set('id', '-1')
            way.set('changeset', changeset)

            #Especificando Nodos del way
            for node in nodes:
                nd = SubElement(way, 'nd')
                nd.set('ref', node.get('id'))

            if osmelement.closed_way == 1:
                nd = SubElement(way, 'nd')
                nd.set('ref', nodes[0].get('id'))

            #Etiqueta de Elemento tipo Way
            tag = SubElement(way, 'tag')
            tag.set('k', osmelement.osm_key)
            tag.set('v', osmelement.osm_value)

            # Obteniendo cadena XML a enviar a OSM
            xmlRequest = str(tostring(root), 'utf-8')

            #return HttpResponse(xmlRequest)

            #Almacendo Elemento en OSM
            client = http.client.HTTPSConnection(osmRestApiUrl)
            client.request('POST', '/api/0.6/changeset/' + changeset + '/upload', xmlRequest, osmHeaders())
            response = client.getresponse()

            if response.status == 200:

                # Cerrar Changeset OSM
                cerrarChangeset(changeset)

                xmlResponse = str(response.read(), 'utf-8')
                xmlObject = ET.fromstring(xmlResponse)
                wayElement = xmlObject.findall('way')[0]

                #Almacenando Cartografia
                user = usuarioAutenticado(request)
                person = models.Person.objects.get(user__userid__exact = user.userid)
                cartografia = almacenarCartografia(instrumento, wayElement.get('new_id'), osmelement, person, tarea)

                response = {
                    'code': 200,
                    #'cartografia': cartografia,
                    'status': 'success'
                }

            else:
                xmlResponse = str(response.read(), 'utf-8')
                raise TypeError("Error al momento de crear el elemento en OSM: " + xmlResponse)

        else:
            raise TypeError("El tipo de instrumento es inválido")

    except ObjectDoesNotExist as e:
        response = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }

    except ValidationError as e:
        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    except json.JSONDecodeError:
        response = {
            'code': 400,
            'message': 'JSON inválido',
            'status': 'error'
        }

    except IntegrityError as e:
        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    except TypeError as e:
        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    # except:
    #     response = {
    #         'code': 500,
    #         'status': 'error'
    #     }

    return JsonResponse(response, status=response['code'])

##
# @brief Funcion que asocia la cartografia realizada en Open Street Maps al sistema
# @param instrid Identificación del Instrumento
# @param wayid Identificación del elemento agregado en Open Street Maps
# @param elemosmid Identificación de tipo de elemento de Open Street Maps
# @param userid Identificación del usuario que realizo la cartografia
# @param tareid Identificación de la tarea
# @return Diccionario con la información de la cartografia realizada
#
def almacenarCartografia(instrument, wayid, osmelement, person, task):
    try:

        cartografia = models.Cartography(instrument=instrument, osmid=wayid, osm_elemtent=osmelement, person=person, task=task)
        cartografia.save()

        return serializers.serialize('python', [cartografia])[0]
    except ObjectDoesNotExist as e:
        response = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }

##
# @brief Recurso que provee los tipos de elementos de Open Street Maps Disponibles
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def elementosOsm(request):

    elementosOsm = models.OsmElement.objects.all().values()

    response = {
        'code': 200,
        'elementosOSM': list(elementosOsm),
        'status': 'success'
    }

    return JsonResponse(response, status=response['code'], safe=False)

##
# @brief Funcion que provee en formato GeoJSON las cartografias realizadas en una tarea
# @param tareid Identificación de la tarea
# @return Diccionario
#
def detalleCartografia(tareid):

    try:
        tarea = models.Task.objects.get(pk=tareid)
        #instrumento = models.Instrument.objects.get(pk = tarea.instrument.instrument_id)
        instrumento = tarea.instrument
        if instrumento.instrument_type == 2:
             
            query = "SELECT c.*, eo.osmelement_name as tipo_elemento_osm, eo.closed_way FROM opx.cartography as c " \
                    "INNER JOIN opx.osm_element as eo ON c.osm_elemtent_id = eo.osmelement_id " \
                    "WHERE c.task_id = '" + tareid + "' " \
                    "AND c.cartography_state <> 0"

            with connection.cursor() as cursor:
                cursor.execute(query)
                cartografias = dictfetchall(cursor)

            if len(cartografias) > 0:

                geometries = []

                #Detalle de Way OSM
                for ct in cartografias:
                    wayHttpClient = http.client.HTTPSConnection(osmRestApiUrl)
                    wayHttpClient.request('GET', '/api/0.6/way/' + ct['osmid'], None, osmHeaders())

                    wayHttpResponse = wayHttpClient.getresponse()

                    if wayHttpResponse.status == 200:
                        xmlResponse = str(wayHttpResponse.read(), 'utf-8')
                        xmlObject = ET.fromstring(xmlResponse)
                        nodes = xmlObject.findall('way')[0].findall('nd')


                        nodesGeometry = []

                        #Detalle de cada uno de los nodos del way
                        for node in nodes:
                            nodeHttpClient = http.client.HTTPSConnection(osmRestApiUrl)
                            nodeHttpClient.request('GET', '/api/0.6/node/' + node.get('ref'), None, osmHeaders())

                            nodeHttpResponse = nodeHttpClient.getresponse()

                            if nodeHttpResponse.status == 200:
                                xmlResponse = str(nodeHttpResponse.read(), 'utf-8')
                                xmlObject = ET.fromstring(xmlResponse)
                                nodeElement = xmlObject.findall('node')[0]

                                # print(xmlResponse)

                                nodesGeometry.append((float(nodeElement.get('lon')), float(nodeElement.get('lat'))))


                            else:
                                raise TypeError("No se pudo obtener información de nodo OSM")

                        if ct['closed_way'] == 1:
                            geometry = Polygon(nodesGeometry)
                        else:
                            geometry = LineString(nodesGeometry)

                        geometries.append(geometry)

                    else:
                        raise TypeError("No se pudo obtener información de way OSM " + str(wayHttpResponse.read(), 'utf-8'))

                geojson = geopandas.GeoSeries(geometries).__geo_interface__

                # Agregando propiedades a cada uno de los Features del GEOJSON
                for index, item in enumerate(geojson['features']):
                    properties = {
                        'id': str(cartografias[index]['cartography_id']),
                        'tipo': cartografias[index]['tipo_elemento_osm']
                    }

                    item['properties'] = properties

                response = {
                    'code': 200,
                    'geojson': json.dumps(geojson),
                    'status': 'success'
                }

            else:
                response = {
                    'code': 200,
                    'geojson': '{"type": "FeatureCollection", "features": []}',
                    'status': 'success'
                }
                #raise ObjectDoesNotExist("No hay cartografias para este instrumento")

        else:
            raise TypeError("Instrumento Inválido")

    except ObjectDoesNotExist as e:
        response = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    except TypeError as e:
        response = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    except:
        response = {
            'code': 500,
            'status': 'error'
        }

    return response

##
# @brief Recurso que provee las cartografias realizadas en una tarea
# @param request Instancia HttpRequest
# @param tareid Identificación de la tarea
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def cartografiasInstrumento(request, tareid):

    response = detalleCartografia(tareid)

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso que elimina un aporte cartográfico del sistema
# @param request Instancia HttpRequest
# @param cartografiaid Identificación de la cartografia
# @return cadena JSON
#
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarCartografia(request, cartografiaid):

    try:
        cartografia = models.Cartography.objects.get(pk = cartografiaid)
        cartografia.estado = 0
        cartografia.save()

        #cartografia.delete()

        response = {
            'code': 200,
            'status': 'success'
        }

    except ObjectDoesNotExist:

        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:

        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, status=response['code'], safe=False)