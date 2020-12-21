"""opc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404, handler500

from myapp import views
from myapp.view import (
    auth,
    equipo,
    proyecto,
    tareas,
    utilidades,
    osm,
    contextualizacion,
    estadisticas,
    plantillaEquipo,
    tiposProyecto
)

urlpatterns = [
    #path('admin/', admin.site.urls),

    path('', views.loginView),
    path('login/', views.login),

    path('auth/password-reset/', auth.passwordReset),
    path('auth/password-reset-verification/', auth.passwordResetVerification),
    path('auth/password-reset/<str:token>', auth.passwordResetConfirmation),
    path('auth/password-reset-done/', auth.passwordResetDone),

    path('usuarios/', views.listadoUsuariosView),
    path('usuarios/list/', views.listadoUsuarios),
    path('usuarios/store/', views.almacenarUsuario),
    path('usuarios/detail/<str:userid>', views.detalleUsuario),
    path('usuarios/delete/<str:userid>', views.eliminarUsuario),
    path('usuarios/<str:userid>', views.actualizarUsuario),

    path('contextos/', views.listadoContextosView),
    path('contextos/list/', views.listadoContextos),
    path('contextos/<str:proyid>/list/', views.listadoContextosProyecto),
    path('contextos/store/', views.almacenamientoContexto),
    path('contextos/delete/<str:contextoid>', views.eliminarContexto),
    path('contextos/<str:contextoid>', views.actualizarContexto),
    path('contextos/datos/<str:contextoid>', views.listadoDatosContextoView),

    path('datos-contexto/list/', views.listadoDatosContextoCompleto),
    path('datos-contexto/list/<str:contextoid>', views.listadoDatosContexto),
    path('datos-contexto/store/', views.almacenarDatoContexto),
    path('datos-contexto/delete/<str:dataid>', views.eliminarDatoContexto),
    path('datos-contexto/<str:dataid>', views.actualizarDatoContexto),

    path('decisiones/', views.listadoDecisionesView),
    path('decisiones/list/', views.listadoDecisiones),
    path('decisiones/<str:proyid>/list/', views.listDecisionesProyecto),
    path('decisiones/store/', views.almacenarDecision),
    path('decisiones/delete/<str:desiid>/', views.eliminarDecision),
    path('decisiones/<str:desiid>', views.actualizarDecision),

    path('decisiones-proyecto/', views.listadoDecisionesProyecto),
    path('decisiones-proyecto/store/', proyecto.almacenarDecisionProyecto),
    path('decisiones-proyecto/delete/<str:desproid>/', views.eliminarDecisionProyecto),
    path('decisiones-proyecto/<str:desproid>', views.actualizarDecisionProyecto),

    path('equipos/', plantillaEquipo.plantillasView),
    path('equipos/<str:planid>/miembros/', plantillaEquipo.miembrosPlantillaView),
    path('equipos/list/<str:proyid>', equipo.equipoProyecto),
    path('equipos/<str:proyid>/usuarios-disponibles/', equipo.usuariosDisponiblesProyecto),
    path('equipos/store/', equipo.almacenamientoEquipo),
    path('equipos/delete/<str:equid>', equipo.eliminarEquipo),
    path('equipos/<str:equid>', equipo.actualizarEquipo),
    path('equipos/proyecto/<str:proyid>', equipo.equipoProyectoView),

    path('plantillas-equipo/list/', plantillaEquipo.listadoPlantillas),
    path('plantillas-equipo/<str:planid>/delete/', plantillaEquipo.eliminarPlantilla),
    path('plantillas-equipo/store/', plantillaEquipo.crearPlantilla),
    path('plantillas-equipo/<str:planid>', plantillaEquipo.edicionPlantilla),

    path('miembros-plantilla/<str:planid>/list/', plantillaEquipo.miembrosPlantilla),
    path('miembros-plantilla/<str:planid>/store/', plantillaEquipo.agregarMiembro),
    path('miembros-plantilla/<str:miplid>/delete/', plantillaEquipo.eliminarMiembro),
    path('miembros-plantilla/<str:planid>/usuarios-disponibles/', plantillaEquipo.miembrosDisponibles),

    path('acciones/list/', views.listadoAcciones),

    path('funciones-rol/list/<str:rolid>', views.listadoFuncionesRol),
    path('funciones-rol/store/', views.almacenamientoFuncionRol),
    path('funciones-rol/delete/<str:funcrolid>', views.eliminarFuncionRol),
    path('funciones-rol/<str:funcrolid>', views.actualizarFuncionRol),

    path('instrumentos/', views.listadoInstrumentosView),
    path('instrumentos/list/', views.listadoInstrumentos),
    path('instrumentos/store/', views.almacenamientoInstrumento),
    path('instrumentos/delete/<str:instrid>', views.eliminarInstrumento),
    path('instrumentos/<str:instrid>', views.actualizarInstrumento),
    path('instrumentos/<str:id>/informacion/', views.informacionInstrumento),
    path('instrumentos/<str:id>/implementar/', views.implementarFormularioKoboToolbox),
    path('instrumentos/<str:id>/verificar-implementacion/', views.verificarImplementaciónFormulario),
    path('instrumentos/encuesta/crear', views.creacionEncuestaView),
    path('instrumentos/formularios-kobotoolbox/list/', views.listadoFormulariosKoboToolbox),
    path('instrumentos/enlace-formulario/<str:tareid>', views.enlaceFormularioKoboToolbox),
    path('instrumentos/mapear/<str:tareid>', osm.AgregarElemento),
    path('instrumentos/detalle-cartografia/<str:tareid>', osm.cartografiasInstrumento),
    path('instrumentos/eliminar-cartografia/<str:cartografiaid>', osm.eliminarCartografia),
    path('instrumentos/revisar-encuesta/<str:encuestaid>', views.revisarEncuesta),

    path('proyectos/', proyecto.listadoProyectosView),
    path('proyectos/gestion/', proyecto.gestionProyectosView),
    path('proyectos/list/', proyecto.listadoProyectos),
    path('proyectos/store/', proyecto.almacenamientoProyecto),
    path('proyectos/delete/<str:proyid>/', proyecto.eliminarProyecto),
    path('proyectos/<str:proyid>', proyecto.actualizarProyecto),
    path('proyectos/detail/<str:proyid>', proyecto.detalleProyecto),
    path('proyectos/dimensiones-territoriales/<str:proyid>', proyecto.dimensionesTerritoriales),
    path('proyectos/<str:proyid>/tareas/', proyecto.tareasProyectoView),
    path('proyectos/<str:dimensionid>/cambio-territorio/', proyecto.cambioTerritorio),

    path('tipos-proyecto/', tiposProyecto.tiposProyectoView),
    path('tipos-proyecto/list/', tiposProyecto.listadoTiposProyecto),
    path('tipos-proyecto/<str:tiproid>/delete/', tiposProyecto.eliminarTipoProyecto),
    path('tipos-proyecto/<str:tiproid>', tiposProyecto.edicionTipoProyecto),
    path('tipos-proyecto/store/', tiposProyecto.almacenamientoTiposProyecto),

    path('roles/', views.listadoRolesView),
    path('roles/list/', views.listadoRoles),
    path('roles/store/', views.almacenamientoRol),
    path('roles/delete/<str:rolid>', views.eliminarRol),
    path('roles/<str:rolid>', views.actualizarRol),
    path('roles/permisos/<str:rolid>', views.permisosRolView),

    path('tareas/', tareas.listadoTareasView),
    path('tareas/list/', tareas.listadoTareas),
    path('tareas/store/', tareas.almacenamientoTarea),
    path('tareas/delete/<str:tareid>/', tareas.eliminarTarea),
    path('tareas/<str:tareid>', tareas.actualizarTarea),
    path('tareas/datos-geoespaciales/', tareas.listadoTareasMapa),
    path('tareas/detail/<str:tareid>', tareas.detalleTarea),
    path('instrumentos/informacion/<str:id>', views.informacionInstrumentoView),
    path('tareas-dimension-territorial/<str:dimensionid>', tareas.tareasXDimensionTerritorial),

    path('generos/list/', utilidades.listadoGeneros),
    path('niveles-educativos/list/', utilidades.listadoNivelesEducativos),
    path('elementos-osm/list/', osm.elementosOsm),

    path('barrios/list/', utilidades.listadoBarrios),

    path('contextualizacion/categorizacion/', contextualizacion.categorizacion),
    path('contextualizacion/todo/', contextualizacion.todo),
    path('contextualizacion/mes/', contextualizacion.mensual),
    path('contextualizacion/semana/', contextualizacion.semanal),
    path('contextualizacion/dia/', contextualizacion.dia),

    # ========================== Estadisticas Antes =================================
    path('estadisticas/datos-generales/', estadisticas.datosGenerales),
    path('estadisticas/usuarios-x-rol/', estadisticas.usuariosXRol),
    path('estadisticas/usuarios-x-genero/', estadisticas.usuariosXGenero),
    path('estadisticas/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativo),
    path('estadisticas/usuarios-x-barrio/', estadisticas.usuariosXBarrio),
    path('estadisticas/ranking/', estadisticas.ranking),
    path('estadisticas/tareas-x-tipo/', estadisticas.tareasXTipo),

    # ======================== Estadisticas Durante ===================================

    path('estadisticas/proyectos-tareas/', estadisticas.proyectosTareas),
    path('estadisticas/estado-proyectos/', estadisticas.estadoActualProyectos),

    # ======================== Estadisticas Después ===================================

    path('estadisticas/proyectos-tareas-vencidos/', estadisticas.proyectosTareasVencidos),
    path('estadisticas/estado-proyectos-vencidos/', estadisticas.estadoActualProyectosVencidos),

    # ======================== Estadísticas - Detalle Proyecto ========================

    path('estadisticas/<str:proyid>/tareas-x-tipo/', estadisticas.tareasXTipoProyecto),
    path('estadisticas/<str:proyid>/tareas-x-estado/', estadisticas.tareasXEstadoProyecto),
    path('estadisticas/<str:proyid>/usuarios-x-rol/', estadisticas.usuariosXRolProyecto),
    path('estadisticas/<str:proyid>/usuarios-x-barrio/', estadisticas.usuariosXBarrioProyecto),
    path('estadisticas/<str:proyid>/usuarios-x-barrio/<str:keyword>', estadisticas.usuariosXBarrioEspecifico),
    path('estadisticas/<str:proyid>/usuarios-x-genero/', estadisticas.usuariosXGeneroProyecto),
    path('estadisticas/<str:proyid>/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativoProyecto),
    path('estadisticas/<str:proyid>/datos-generales/', estadisticas.datosGeneralesProyecto),
    path('estadisticas/<str:proyid>/exportar-encuestas/', estadisticas.exportarDatos),
    path('estadisticas/<str:proyid>/exportar-proyecto/', estadisticas.exportarDatosProyecto),
    path('estadisticas/<str:proyid>/ranking/', estadisticas.rankingPorProyecto),
    path('estadisticas/<str:proyid>/campanas/', estadisticas.dimensionesProyecto),
    path('estadisticas/<str:dimensionid>/tareas-campana/', estadisticas.tareasDimensionProyecto),
    path('estadisticas/<str:proyid>/instrumentos/', estadisticas.instrumentosProyecto),

    # ========================= Vista Estadísticas =====================================

    path('reportes/antes/', estadisticas.estadisticasView),
    path('reportes/durante/', estadisticas.estadisticasDuranteView),
    path('reportes/despues/', estadisticas.estadisticasDespuesView),
    path('reportes/<str:proyid>/detalle/', estadisticas.estadisticasDetalleView),
    path('reportes/ranking/', estadisticas.rankingView),

    # =========================== Perfil ===============================================
    path('mi-perfil/', views.perfilView)
]

handler404 = utilidades.notFoundPage
handler500 = utilidades.serverErrorPage