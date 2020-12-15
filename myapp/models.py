from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid

class MyUserManager(BaseUserManager):
    use_in_migrations = True

##
# @brief Modelo de usuario
#
class Usuario(AbstractBaseUser):
    userid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    useremail = models.EmailField(max_length = 255, unique=True)
    password = models.CharField(max_length = 255)
    usertoken = models.CharField(max_length = 255, null = True, blank = True)
    userfullname = models.CharField(max_length = 255, null=True)
    rolid = models.UUIDField(null=True)
    userleveltype = models.IntegerField(null=True)
    userestado = models.IntegerField(null=True)
    fecha_nacimiento = models.DateField(null=True)
    generoid = models.UUIDField(null=True)
    barrioid = models.IntegerField(null=True)
    nivel_educativo_id = models.UUIDField(null=True)
    telefono = models.CharField(max_length=20, null=True)
    latitud = models.CharField(blank=True, null=True, max_length=30)
    longitud = models.CharField(blank=True, null=True, max_length=30)
    horaubicacion = models.CharField(blank=True, null=True, max_length=100)
    puntaje = models.IntegerField(null=True, blank=True, default=0)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    empleado = models.IntegerField(blank=True, default=0, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = "useremail"

    class Meta:
        db_table = '"v1"."usuarios"'

##
# @brief Modelo de Contextos
#
class Contexto(models.Model):

    contextoid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    descripcion = models.CharField(max_length = 1000)

    class Meta:
        db_table = '"v1"."contextos"'

##
# @brief Modelo de Datos de Contexto
#
class DatosContexto(models.Model):

    dataid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    hdxtag = models.CharField(max_length = 100)
    datavalor = models.CharField(max_length = 100)
    datatipe = models.CharField(max_length=100)
    contextoid = models.UUIDField()
    descripcion = models.CharField(max_length=500, null=True)
    geojson = models.CharField(max_length=3000, null=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = '"v1"."datos_contexto"'

##
# @brief Modelo de Contextos Proyecto
#
class ContextoProyecto(models.Model):

    contproyid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    proyid = models.UUIDField(null=True)
    contextoid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."contextos_proyecto"'

##
# @brief Modelo de Decisiones
#
class Decision(models.Model):
    desiid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    desidescripcion = models.CharField(max_length = 1000)
    userid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."decisiones"'

##
# @brief Modelo de Decisiones Proyecto
#
class DecisionProyecto(models.Model):
    desproid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    proyid = models.UUIDField(null=True)
    desiid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."decisiones_proyecto"'

##
# @brief Modelo de Equipos
#
class Equipo(models.Model):
    equid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    userid = models.UUIDField(null=True)
    proyid = models.UUIDField(null=True)
    miembroestado = models.IntegerField(default=1)

    class Meta:
        db_table = '"v1"."equipos"'

##
# @brief Modelo de Permisos del Sistema
#
class Accion(models.Model):
    accionid = models.UUIDField(primary_key= True, default = uuid.uuid4(), editable = False)
    nombre = models.CharField(max_length = 255)
    descripcion = models.CharField(max_length = 1000)

    class Meta:
        db_table = '"v1"."acciones"'

##
# @brief Modelo de permisos para los roles
#
class FuncionRol(models.Model):
    funcrolid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    rolid = models.UUIDField(null=True)
    accionid = models.CharField(max_length = 255, null=True)
    funcrolestado = models.IntegerField()
    funcrolpermiso = models.IntegerField()

    class Meta:
        db_table = '"v1"."funciones_rol"'

##
# @brief Modelo de instrumentos
#
class Instrumento(models.Model):
    instrid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    instridexterno = models.CharField(max_length = 255)
    instrtipo = models.IntegerField()
    instrnombre = models.CharField(max_length = 255)
    instrdescripcion = models.CharField(max_length = 3000, null = True, blank = True)
    geojson = models.CharField(max_length=1000, null = True, blank=True)

    class Meta:
        db_table = '"v1"."instrumentos"'

##
# @brief Modelo de Proyectos
#
class Proyecto(models.Model):
    proyid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    proynombre = models.CharField(max_length = 255)
    proydescripcion = models.TextField()
    proyidexterno = models.CharField(max_length = 255)
    proyfechacreacion = models.CharField(max_length=100)
    proyfechacierre = models.DateField(null=True, blank=True)
    proyestado = models.IntegerField()
    proypropietario = models.UUIDField(null=True)
    proyfechainicio = models.DateField(null=True, blank=True)
    tiproid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."proyectos"'

##
# @brief Modelo de Roles del sistema
#
class Rol(models.Model):
    rolid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    rolname = models.CharField(max_length=50)
    roldescripcion = models.CharField(max_length = 255)
    rolestado = models.IntegerField()

    class Meta:
        db_table = '"v1"."roles"'

##
# @brief Modelo de Tareas
#
class Tarea(models.Model):

    tareid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    tarenombre = models.CharField(max_length = 255)
    taretipo = models.IntegerField(null=True)
    tarerestricgeo = models.CharField(max_length = 1000)
    tarerestriccant = models.IntegerField(null=True)
    tarerestrictime = models.CharField(max_length = 1000)
    instrid = models.UUIDField(null=True)
    proyid = models.UUIDField(null=True)
    dimensionid = models.UUIDField(null=True, blank=True)
    geojson_subconjunto = models.CharField(max_length=1000, null=True)
    tarefechacreacion = models.DateTimeField(null = True, blank = True, default=datetime.today())
    taredescripcion = models.TextField(null=True)
    tareestado = models.IntegerField(default=0)
    observaciones = models.TextField(blank = True, null = True)
    tareprioridad = models.IntegerField(null=True)

    class Meta:
        db_table = '"v1"."tareas"'

##
# @brief Modelo de Dimensiones Geográficas
#
class DelimitacionGeografica(models.Model):

    dimensionid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyid = models.UUIDField(null=True)
    nombre = models.CharField(max_length=255, null=True)
    geojson = models.CharField(max_length=1000, null=True)
    estado = models.IntegerField(default=1)

    class Meta:
        db_table = '"v1"."dimensiones_territoriales"'

##
# @brief Modelo de Generos
#
class Genero(models.Model):

    generoid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = '"v1"."generos"'

##
# @brief Modelo de Niveles educativos
#
class NivelEducativo(models.Model):

    nivelid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = '"v1"."niveles_educativos"'

##
# @brief Modelo de barrios
#
class Barrio(models.Model):

    barrioid = models.IntegerField(editable=False, primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = '"v1"."barrios"'

##
# @brief Modelo de cartografias
#
class Cartografia(models.Model):

    cartografiaid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    instrid = models.UUIDField(null=True)
    osmid = models.CharField(max_length=255)
    elemosmid = models.UUIDField(null=True)
    userid = models.UUIDField(null=True)
    estado = models.IntegerField(default=0)
    tareid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."cartografias"'

##
# @brief Modelo de elementos de Open Street Maps
#
class ElementoOsm(models.Model):

    elemosmid = models.UUIDField(editable=False, primary_key=True)
    nombre = models.CharField(max_length=255)
    llaveosm = models.CharField(max_length=255)
    valorosm = models.CharField(max_length=255)
    closed_way = models.IntegerField()

    class Meta:
        db_table = '"v1"."elementos_osm"'

##
# @brief Modelo de Encuestas
#
class Encuesta(models.Model):
    
    encuestaid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    instrid = models.UUIDField(null=True)
    koboid = models.UUIDField(null=True)
    contenido = models.CharField(max_length=5000)
    estado = models.IntegerField(default=0)
    observacion = models.CharField(blank=True, max_length=3000, null=True)
    userid = models.UUIDField(null=True)
    tareid = models.UUIDField(null=True)
    
    class Meta:
        db_table = '"v1"."encuestas"'

##
# @brief Modelo de Conflictividades
#
class Conflictividad(models.Model):

    confid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = '"v1"."conflictividades"'

##
# @brief Modelo de los hechos asociados a las conflictividades
#
class Contextualizacion(models.Model):

    contxtid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    fecha_hecho = models.DateField()
    hora_hecho = models.TimeField()
    dia = models.IntegerField()
    confid = models.UUIDField(null=True)
    generoid = models.UUIDField(null=True)
    edad = models.IntegerField()
    nivelid = models.UUIDField(null=True)
    nombre_barrio = models.CharField(max_length=300)
    cantidad = models.IntegerField(null=True)
    barrioid = models.IntegerField(null=True)

    class Meta:
        db_table = '"v1"."contextualizaciones"'

##
# @brief Modelo de parámetros del sistema
#
class  Parametro(models.Model):

    paramid = models.CharField(max_length=1000, primary_key=True)
    paramvalor = models.CharField(max_length=1000)
    paramdesc = models.CharField(max_length=1000)

    class Meta:
        db_table = '"v1"."parametros"'

##
# @brief Modelo de historial de asignaciones de puntaje
#
class AsignacionPuntaje(models.Model):

    asigid = models.UUIDField(default = uuid.uuid4, primary_key=True)
    userid = models.UUIDField(null=True)
    tareid = models.UUIDField(null=True)
    puntaje = models.IntegerField()

    class Meta:
        db_table = '"v1"."asignaciones_puntajes"'

##
# @brief Modelo de plantillas de equipo
#
class PlantillaEquipo(models.Model):

    planid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    descripcion = models.TextField()
    userid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."plantillas_equipo"'

##
# @brief Modelo de miembros de plantilla
#
class MiembroPlantilla(models.Model):

    miplid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    userid = models.UUIDField(null=True)
    estado = models.IntegerField(default=1)
    planid = models.UUIDField(null=True)

    class Meta:
        db_table = '"v1"."miembros_plantilla"'

##
# @brief Modelo de Tipos de Proyecto
#
class TipoProyecto(models.Model):

    tiproid = models.UUIDField(default = uuid.uuid4, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        db_table = '"v1"."tipos_proyecto"'