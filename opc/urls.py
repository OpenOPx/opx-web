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
    userview, instrumentview, koboclient, auth, proyecto, decision, equipo, comentario, equipoMiembros, notificaciones,
    utilidades, osm, rolesview, tiposProyecto, profileview, estadisticas, contextoview, tareas, reporte, encuestaview, territorialDimension, #,contextualizacion, tareas
)

urlpatterns = [

#los id's los pasan por el path y deberian pasarlos internamente

    path('admin/', admin.site.urls), 

    path('', views.loginView), #OK OK LEO
    path('login/', views.login), #OK OK LEO

    path('auth/password-reset/', auth.passwordReset), #OK OK LEO
    path('auth/password-reset-verification/', auth.passwordResetVerification), #O OK LEO
    path('auth/password-reset/<str:token>', auth.passwordResetConfirmation), #OK OK LEO
    path('auth/password-reset-done/', auth.passwordResetDone), #Ok OK LEO 

    path('usuarios/', userview.listadoUsuariosView), #OK OK LEO 
    path('usuarios/list/', userview.listadoUsuarios), #OK OK LEO
    path('usuarios/store/', userview.almacenarUsuario), #OK OK LEO
    path('usuarios/detail/<str:userid>', userview.detalleUsuario), #OK OK LEO
    path('usuarios/delete/<str:userid>', userview.eliminarUsuario), #OK OK LEO
    path('usuarios/<str:userid>', userview.actualizarUsuario), #OK OK LEO

    path('contextos/', contextoview.listadoContextosView), #OK OK 
    path('contextos/list/', contextoview.listadoContextos), #OK OK S
    path('contextos/store/', contextoview.almacenamientoContexto), #OK OK S
    path('contextos/delete/<str:contextoid>', contextoview.eliminarContexto), #OK S 
    path('contextos/<str:contextoid>', contextoview.actualizarContexto), #OK OK S
    path('contextos/datos/<str:contextoid>', contextoview.listadoDatosContextoView), #OK OK S
    path('contextos/<str:proyid>/list/', contextoview.listadoContextosProyecto), #OK OK S

    path('datos-contexto/list/', contextoview.listadoDatosContextoCompleto), #OK OK S
    path('datos-contexto/list/<str:contextoid>', contextoview.listadoDatosContexto), #OK OK S
    path('datos-contexto/store/', contextoview.almacenarDatoContexto), #OK OK S
    path('datos-contexto/delete/<str:dataid>', contextoview.eliminarDatoContexto), #OK OK S
    path('datos-contexto/<str:dataid>', contextoview.actualizarDatoContexto), #OK OK S

    path('decisiones/', decision.listadoDecisionesView), #OK OK JM
    path('decisiones/list/', decision.listadoDecisiones), #OK OK JM
    path('decisiones/store/', decision.almacenarDecision), #OK OK JM
    path('decisiones/delete/<str:desiid>/', decision.eliminarDecision), #OK OK JM
    path('decisiones/<str:desiid>', decision.actualizarDecision), #OK OK JM


    path('equipos/', equipo.equiposView), #OK OK JM
    path('equipos/<str:planid>/miembros/', equipo.miembrosEquipoView), #OK OK JM
    path('plantillas-equipo/list/', equipo.listadoEquipos), #OK OK JM
    path('plantillas-equipo/<str:planid>/delete/', equipo.eliminarEquipo), #OK OK JM
    path('plantillas-equipo/store/', equipo.crearEquipo), #OK OK JM
    path('plantillas-equipo/<str:planid>/', equipo.actualizarEquipo), #OK OK JM
 
    path('miembros-plantilla/<str:planid>/list/', equipoMiembros.listadoMiembros), #OK OK JM
    path('miembros-plantilla/<str:planid>/store/', equipoMiembros.agregarMiembro), #OK OK JM
    path('miembros-plantilla/<str:miplid>/delete/', equipoMiembros.eliminarMiembro), #OK OK JM
    path('miembros-plantilla/<str:planid>/usuarios-disponibles/', equipoMiembros.miembrosDisponibles), #OK OK JM

    path('acciones/list/', rolesview.listadoAcciones), #OK OK S

    path('funciones-rol/list/<str:rolid>', rolesview.listadoFuncionesRol), #OK OK S
    path('funciones-rol/store/', rolesview.almacenamientoFuncionRol), #OK OK S
    path('funciones-rol/delete/<str:funcrolid>', rolesview.eliminarFuncionRol), #OK OK S

    path('instrumentos/', instrumentview.listadoInstrumentosView), #OK OK LEO
    path('instrumentos/list/', instrumentview.listadoInstrumentos), #OK OK LEO
    path('instrumentos/store/', instrumentview.almacenamientoInstrumento), #OK OK LEO
    path('instrumentos/<str:instrid>', instrumentview.actualizarInstrumento), #OK OK LEO
    path('instrumentos/<str:id>/implementar/', koboclient.implementarFormularioKoboToolbox), #OK OK LEO
    path('instrumentos/<str:id>/verificar-implementacion/', koboclient.verificarImplementaciónFormulario), #OK OK LEO

    #path('instrumentos/delete/<str:instrid>', views.eliminarInstrumento), #??? ESTO ALGUNA VEZ ESTUVO? - El back de NM tiene eliminar instrumento
    path('instrumentos/<str:id>/informacion/', instrumentview.informacionInstrumento), #??? - El back de NM tiene esto instrumento

    path('instrumentos/formularios-kobotoolbox/list/', koboclient.listadoFormulariosKoboToolbox), #OK OK LEO
    path('instrumentos/enlace-formulario/<str:tareid>', koboclient.enlaceFormularioKoboToolbox), #OK OK LEO

    path('instrumentos/mapear/<str:tareid>', osm.AgregarElemento), # ok LF
    path('instrumentos/detalle-cartografia/<str:tareid>', osm.cartografiasInstrumento), # OK LF
    path('instrumentos/eliminar-cartografia/<str:cartografiaid>', osm.eliminarCartografia), # ok LF
    path('instrumentos/revisar-encuesta/<str:encuestaid>', encuestaview.revisarEncuesta), #???
    path('instrumentos/kobo-submissions/<str:tareaid>', koboclient.koboSubmissionsQuantity),
    path('instrumentos/encuesta/store/', koboclient.almacenarSurvery),

    path('equipos/list/<str:proyid>', proyecto.equipoProyecto), #OK OK JM
    path('equipos/<str:proyid>/equipos-disponibles/', proyecto.equiposDisponiblesProyecto), #OK OK JM
    path('equipos/store/', proyecto.agregarEquipo), #OK OK JM
    path('equipos/delete/<str:equid>', proyecto.eliminarEquipo), #OK OK JM
    path('equipos/proyecto/<str:proyid>', proyecto.equipoProyectoView), #OK OK JM
    path('proyectos/', proyecto.listadoProyectosView), #OK OK JM
    path('proyectos/gestion/', proyecto.gestionProyectosView), #OK OK JM
    path('proyectos/list/', proyecto.listadoProyectos), #OK OK JM
    path('proyectos/store/', proyecto.almacenamientoProyecto), #OK OK JM
    path('proyectos/delete/<str:proyid>/', proyecto.eliminarProyecto), #OK OK JM
    path('proyectos/<str:proyid>', proyecto.actualizarProyecto), #OK OK JM
    path('proyectos/basic-update/<str:proyid>', proyecto.actualizarProyectoBasic), #OK OK JM
    path('proyectos/details/<str:proyid>', proyecto.detalleProyecto), #OK OK JM
    path('proyectos/detail/<str:proyid>', proyecto.detalleProyectoMovil), #OK OK JM
    path('proyectos/<str:proyid>/tareas/', proyecto.tareasProyectoView), #OK OK JM
    path('proyectos/dimensiones-territoriales/<str:proyid>', proyecto.dimensionesTerritoriales), #OK OK JM
    path('decisiones/reportes/<str:proyid>', proyecto.decisionesDelProyecto),

    path('proyectos/<str:dimensionid>/cambio-territorio/', proyecto.cambioTerritorio), #LEO

    path('tipos-proyecto/', tiposProyecto.tiposProyectoView), #OK OK S
    path('tipos-proyecto/list/', tiposProyecto.listadoTiposProyecto), #OK OK S 
    path('tipos-proyecto/<str:tiproid>/delete/', tiposProyecto.eliminarTipoProyecto),#OK OK S
    path('tipos-proyecto/<str:tiproid>', tiposProyecto.edicionTipoProyecto), #OK OK S
    path('tipos-proyecto/store/', tiposProyecto.almacenamientoTiposProyecto), #OK OK S

    path('roles/', rolesview.listadoRolesView), #OK OK S
    path('roles/list/', rolesview.listadoRoles), #OK OK S

    path('roles/permisos/<str:rolid>', rolesview.permisosRolView), #OK OK S

    path('tareas/', tareas.listadoTareasView), #OK S OK
    path('tareas/list/', tareas.listadoTareas), #OK S
    path('tareas/delete/<str:tareid>/', tareas.eliminarTarea), #OK S OK
    path('tareas/store/', tareas.almacenamientoTarea), #OK S
    path('tareas/campana/', tareas.almacenamientoCampana), #OK S
    path('tareas/<str:tareid>', tareas.actualizarTarea), #OK S OK
    path('tareas/gestion-cambios/<str:tareid>', tareas.actualizarTareaGestionCambios), #OK S OK
    #path('tareas/datos-geoespaciales/', tareas.listadoTareasMapa), #S #???
    path('tareas/detail/<str:tareid>', tareas.detalleTarea), #OK S OK
    path('instrumentos/informacion/<str:id>', instrumentview.informacionInstrumentoView), #S #???
    #path('tareas-dimension-territorial/<str:dimensionid>', tareas.tareasXDimensionTerritorial), #S #??? Se usaba en GC pero ya no (LFC)
    path('tareas/tipos/', views.listadoTiposDeTareas), #OK S

    path('generos/list/', utilidades.listadoGeneros), #OK OK S
    path('niveles-educativos/list/', utilidades.listadoNivelesEducativos), #OK OK S
    path('elementos-osm/list/', osm.elementosOsm),  #S JM LEO



    path('barrios/list/', utilidades.listadoBarrios), #OK OK S
    path('tareas/store/', tareas.almacenamientoTarea), #OK - JM
    #path('contextualizacion/categorizacion/', contextualizacion.categorizacion), # Reportes?
    #path('contextualizacion/todo/', contextualizacion.todo), #Reportes?
    #path('contextualizacion/mes/', contextualizacion.mensual), #Reportes?
    #path('contextualizacion/semana/', contextualizacion.semanal), #Reportes?
    #path('contextualizacion/dia/', contextualizacion.dia), #Reportes?

    path('comentario/list/<str:projid>', comentario.listadoComentarios), #OK - JM 
    path('comentario/delete/<str:comid>', comentario.eliminarComentario), #OK - JM 
    path('comentario/store/<str:projid>', comentario.crearComentario), #OK - JM 
    path('comentario/update/', comentario.actualizarComentario), #OK - JM 
    
    #pendiente
    path('reportes/equipos/', reporte.reporteEquiposView), #JM OK OK
    path('reportes/equipos/estadisticas/1/', reporte.canva1), #JM OK OK
    path('reportes/equipos/estadisticas/2/', reporte.canva2), #JM OK OK
    path('reportes/equipos/estadisticas/3/', reporte.canva3), #JM OK OK
    path('reportes/equipos/estadisticas/generales/', reporte.generales), #JM OK OK
    path('reportes/equipos/<str:planid>/miembros/', reporte.miembrosEquipoView), #JM OK OK
    path('reportes/equipos/miembro/<str:personId>/equipos/', reporte.equiposPersona), #JM OK OK
    path('reportes/equipos/miembro/<str:personId>/proyectos/', reporte.proyectosPersona), #JM OK OK
    path('reportes/equipos/miembro/<str:personId>/', reporte.reporteMiembroView), #JM OK OK
    path('persona/detalle/<str:personId>/', reporte.detallePersona), #JM OK OK
    path('reportes/rank/', reporte.ranking), #JM OK
    path('reportes/ranking/', reporte.reporteRankView), #JM
    path('puntaje/tarea/<str:tarid>/', utilidades.puntajeTarea), #JM - S
    path('puntaje/proyecto/<str:proyid>/', utilidades.puntajeProyecto), #JM - S

    path('dimensionesPre/', proyecto.listaDimensionesPrecargadas),
    path('proyectos/dimensionesPre/mapa/', proyecto.mapaDimension),

    # ========================== Estadisticas Antes =================================
    path('estadisticas/datos-generales/', estadisticas.datosGenerales), #OK - S PROBAR
    path('estadisticas/usuarios-x-rol/', estadisticas.usuariosXRol), #OK - S PROBAR
    path('estadisticas/usuarios-x-genero/', estadisticas.usuariosXGenero), #OK - S PROBAR
    path('estadisticas/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativo), #OK - S PROBAR (OJO CON ESE NOMBRE EN LA IMAGEN DEL MODELO QUE NO ME LO VAYA A CAMBIAR)
    path('estadisticas/usuarios-x-barrio/', estadisticas.usuariosXBarrio), #OK - S PROBAR
    path('estadisticas/ranking/', estadisticas.ranking),  #OK - S PROBAR 
    path('estadisticas/tareas-x-tipo/', estadisticas.tareasXTipo), #OK - S OJO CON LOS CAMBIOS A HACER

    # ======================== Estadisticas Durante ===================================

    path('estadisticas/proyectos-tareas/', estadisticas.proyectosTareas), # QUEDÉ EN LA PARTE DE ENCUESTAS Y PROGRESO - S

    #path('estadisticas/estado-proyectos/', estadisticas.estadoActualProyectos), # AHORA QUE ME ACUERDO ESTO NO SE VA A USAR 

    # ======================== Estadisticas Después ===================================

    #path('estadisticas/proyectos-tareas-vencidos/', estadisticas.proyectosTareasVencidos),
    #path('estadisticas/estado-proyectos-vencidos/', estadisticas.estadoActualProyectosVencidos),

    # ======================== Estadísticas - Detalle Proyecto ========================

    #path('estadisticas/<str:proyid>/tareas-x-tipo/', estadisticas.tareasXTipoProyecto),
    #path('estadisticas/<str:proyid>/tareas-x-estado/', estadisticas.tareasXEstadoProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-rol/', estadisticas.usuariosXRolProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-barrio/', estadisticas.usuariosXBarrioProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-barrio/<str:keyword>', estadisticas.usuariosXBarrioEspecifico),
    #path('estadisticas/<str:proyid>/usuarios-x-genero/', estadisticas.usuariosXGeneroProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativoProyecto),
    #path('estadisticas/<str:proyid>/datos-generales/', estadisticas.datosGeneralesProyecto),
    #path('estadisticas/<str:proyid>/exportar-encuestas/', estadisticas.exportarDatos),
    #path('estadisticas/<str:proyid>/exportar-proyecto/', estadisticas.exportarDatosProyecto),
    #path('estadisticas/<str:proyid>/ranking/', estadisticas.rankingPorProyecto),
    #path('estadisticas/<str:proyid>/campanas/', estadisticas.dimensionesProyecto),
    #path('estadisticas/<str:dimensionid>/tareas-campana/', estadisticas.tareasDimensionProyecto),
    #path('estadisticas/<str:proyid>/instrumentos/', estadisticas.instrumentosProyecto),

    # ========================= Vista Estadísticas =====================================

    path('reportes/antes/', estadisticas.estadisticasView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/durante/', estadisticas.estadisticasDuranteView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/despues/', estadisticas.estadisticasDespuesView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/<str:proyid>/detalle/', estadisticas.estadisticasDetalleView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/proyectos/', estadisticas.estadisticasProyectosView),   
    path('reportes/proyecto/<str:projid>', estadisticas.proyectoIndividualView),


    #path('reportes/ranking/', estadisticas.rankingView),  #S - Vistas que se agregan después por nuestra funcionalidad
    #path('reportes/proyecto/', estadisticas.reportesProyectosIndividualesView), #S - Vistas que se agregan después por nuestra funcionalidad
    #path('reportes/proyectos/', estadisticas.reportesProyectosGeneralesView),  #S - Vistas que se agregan después por nuestra funcionalidad

    # =========================== Perfil ===============================================
    path('mi-perfil/', profileview.perfilView), #OK OK LEO

    path('external-platforms/kobo-kpi/', koboclient.getKoboKpiUrl), #OK OK LEO
    path('notificaciones/list/', notificaciones.getPersonNotifications), # LF Gestion de cambios
    path('notificaciones/delete/', notificaciones.deletePersonNotifications),
    #=========================== Dimensiones ===============================================
    path('dimensiones/barrios/', territorialDimension.listadoDimensionesBarrios),
    path('dimensiones/<str:dimension_id>', territorialDimension.getDimensionPreloaded),
    path('proyectos/gestion/dimensiones/<str:dimension_id>/geojson/', territorialDimension.updateGeojson),
]
