let tarea = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-tareas',
    created(){

        if(window.location.pathname == '/tareas/'){

            this.listadoTareas();
            this.listadoProyectos();

            this.general = true;

        } else if(window.location.pathname.substr(48,6) == "tareas"){

            this.proyectoID = window.location.pathname.substr(11, 36)

            this.listadoTareasProyecto(this.proyectoID)
            this.listadoProyectos();

            this.general = false;
        }
    },
    data: {
        tareas: [],
        edicionTarea: {},
        almacenamientoTarea: {
            geojsonsubconjunto: null
        },
        proyectos: [],
        instrumentos: [],
        loading: false,
        campana: false,
        dimensionesTerritoriales: [],
        taskMap: {},
        dimensionTerritorialReferencia: {},
        filterKey: '',
        general: true,
        proyectoID: null,
        // Datos de Paginación
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        // Busqueda
        filtro: '',
        // Campos Tareas
        tareasFields: [
            {
                label: 'Nombre',
                key: 'task_name',
                sortable: true
            },
            {
                label: 'Tipo',
                key: 'task_type_name',
                sortable: true
            },
            {
                label: 'Cantidad',
                key: 'task_quantity',
                sortable: true
            },
            {
                label: 'Completitud (%)',
                key: 'task_completness'
            },
            {
                label: 'Proyecto',
                key: 'proj_name'
            },
            {
                label: 'Prioridad',
                key: 'priority_name'
            },
            {
                label: 'Fecha de Creación',
                key: 'task_creation_date'
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    methods: {
        cambiarCampana(campana){
            this.campana = campana
        },
        listadoTareas(){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/tareas/list/',
                params: {
                    all: 1
                },
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.loader(false);

                if(response.data.code == 200 && response.data.status == 'success'){
                    this.tareas = response.data.tareas;
                }
            });
        },
        listadoTareasProyecto(proyectoid){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/proyectos/details/' + proyectoid,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.loader(false);

                if(response.data.code == 200 && response.data.status == 'success'){
                    this.tareas = response.data.detail.tareas;
                }
            });
        },
        almacenarTarea(){

            this.loader(true);

            var queryString = Object.keys(this.almacenamientoTarea).map(key => {

                if(key == 'dimensionid' && this.almacenamientoTarea.taretipo == "1"){

                    valor = (this.almacenamientoTarea.dimensionid).dimension_id;

                } else if(key == 'instrid'){

                    valor = this.almacenamientoTarea.instrid

                } else{

                    valor = this.almacenamientoTarea[key];
                }

                return key + '=' + valor;
            }).join('&');

            axios({
                method: 'post',
                url: '/tareas/store/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-tarea").modal('hide')
                this.almacenamientoTarea = {
                    geojsonsubconjunto: null
                };
                this.restablecerMapa();

                if(this.general){

                    this.listadoTareas();

                } else{

                    this.listadoTareasProyecto(this.proyectoID);
                }


                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Tarea creada satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(response => {

                $("#agregar-tarea").modal('hide')
                this.almacenamientoTarea = {
                    geojsonsubconjunto: null
                };
                this.restablecerMapa();
                this.almacenamientoProyecto.tarfechainicio = null;
                this.almacenamientoProyecto.tarfechacierre= null;
                this.loader(false);
                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        almacenarCampana(){
            this.loader(true);

            var queryString = Object.keys(this.almacenamientoTarea).map(key => {

                if(key == 'dimensionid' && this.almacenamientoTarea.task_type_id == "1"){

                    valor = (this.almacenamientoTarea.dimensionid).dimension_id;

                } else if(key == 'instrument_id'){

                    valor = this.almacenamientoTarea.instrument_id

                } else{

                    valor = this.almacenamientoTarea[key];
                }

                return key + '=' + valor;
            }).join('&');

            axios({
                method: 'post',
                url: '/tareas/campana/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-tarea").modal('hide')
                this.almacenamientoTarea = {
                    geojsonsubconjunto: null
                };
                this.restablecerMapa();

                if(this.general){

                    this.listadoTareas();

                } else{

                    this.listadoTareasProyecto(this.proyectoID);
                }


                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Tarea creada satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(response => {

                $("#agregar-tarea").modal('hide')
                this.almacenamientoTarea = {
                    geojsonsubconjunto: null
                };
                this.restablecerMapa();

                this.loader(false);
                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        eliminarTarea(id){

            Swal.fire({
              title: 'Estas seguro?',
              text: "No lo puedes revertir",
              type: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#3085d6',
              cancelButtonColor: '#d33',
              confirmButtonText: 'Acepto!'

            }).then((result) => {

              if (result.value) {

                this.loader(true);

                axios({
                    method: 'DELETE',
                    url: '/tareas/delete/' + id,
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.loader(false);

                    if(this.general){

                        this.listadoTareas();

                    } else{

                        this.listadoTareasProyecto(this.proyectoID)
                    }


                    Swal.fire(
                      'Eliminado!',
                      'La tarea fue eliminada de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     if(this.general){

                        this.listadoTareas();

                     } else{

                        this.listadoTareasProyecto(this.proyectoID)
                    }

                     this.loader(false);

                     Swal.fire(
                      'Error!',
                      'Ocurrio un error por favor intenta de nuevo',
                      'error'
                    );
                });
              }
            });
        },
        editarTarea(){

            this.loader(true);

            var queryString = Object.keys(this.edicionTarea).map(key => {

                let valor = "";

                if(key == 'tarerestricgeo' && typeof this.edicionTarea.tarerestricgeo == 'object'){

                    valor = JSON.stringify(this.edicionTarea.tarerestricgeo);

                } else if(key == 'tarerestrictime' && typeof this.edicionTarea.tarerestrictime == 'object'){

                    valor = JSON.stringify(this.edicionTarea.tarerestrictime);

                } else{

                    valor = this.edicionTarea[key];
                }

                return key + '=' + valor;

            }).join('&');
            axios({
                method: 'post',
                url: '/tareas/' + this.edicionTarea.task_id,
                data: queryString,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#editar-tarea").modal('hide');

                if(this.general){

                    this.listadoTareas();

                } else{

                    this.listadoTareasProyecto(this.proyectoID)
                }
                this.loader(false);

                Swal.fire(
                    'Exito!',
                    'Tarea modificada satisfactoriamente',
                    'success'
                );
            })
            .catch(() => {

                $("#editar-tarea").modal('hide');
                this.loader(false);

                Swal.fire(
                    'Error!',
                    'Ocurrio un error. Por favor intenta de nuevo',
                    'error'
                );
            });
        },
        listadoProyectos(){

            axios({
                method: 'GET',
                url: '/proyectos/list/',
                params: {
                    all: 1
                },
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.proyectos = response.data.proyectos;
                }
            });
        },
        listadoInstrumentos(instrtipo){

            axios({
                method: 'GET',
                url: '/instrumentos/list/',
                params: {
                    instrtipo: instrtipo
                },
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

              this.instrumentos = response.data;
            });
        },
        loader(status){

            this.loading = status;
        },
        obtenerDimensionesTerritoriales(proyid){
            
            axios({
                url: '/proyectos/dimensiones-territoriales/' + proyid,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.dimensionesTerritoriales = response.data.dimensionesTerritoriales;

                    if(this.almacenamientoTarea.taretipo == "1"){

                        this.restablecerMapa();
                    }
                }
            })
        },
        generarMapa(timeout, dimension){
            
            window.setTimeout(() => {
                
                var taskMap = L.map('taskmap',  {
                    center: [3.450572, -76.538705],
                    drawControl: false,
                    zoom: 13
                });
                
                L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
                  attribution: 'idesccali.gov.co © IDESC',
                }).addTo(taskMap);

                L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
                  layers: 'idesc:mc_barrios',
                  format: 'image/png',
                  transparent: !0,
                  version: '1.1.0'
                }).addTo(taskMap);
                if(dimension){
                    this.dimensionTerritorialReferencia = L.polygon(this.obtenerCoordenadas(dimension.dimension_geojson)).addTo(taskMap);

                    //L.marker([3.45000, -76.535000]).addTo(taskMap);

                    var editableLayers = new L.FeatureGroup();

                    taskMap.addLayer(editableLayers);

                    var options = {
                        // position: 'topright',
                        draw: {
                            polygon: {
                                allowIntersection: true, // Restricts shapes to simple polygons
                                drawError: {
                                    color: '#e1e100', // Color the shape will turn when intersects
                                    message: '<strong>Oh snap!</strong> you can\'t draw that!' // Message that will show when intersect
                                },
                                shapeOptions: {
                                    color: '#0CBAEF'
                                }
                            },
                            polyline: false,
                            circle: false, // Turns off this drawing tool
                            rectangle: false,
                            marker: false,
                            circlemaker: false
                        },
                        edit: {
                            featureGroup: editableLayers, //REQUIRED!!
                            //remove: false
                        }
                    };

                    var drawControl = new L.Control.Draw(options);

                    taskMap.addControl(drawControl);

                    taskMap.on(L.Draw.Event.CREATED, (e) => {
                        type = e.layerType;
                        layer = e.layer;

                        if (type === 'polygon' && this.cantidadAreasMapa(editableLayers) == 0 && this.validarSubconjunto(layer.toGeoJSON())) {

                            editableLayers.addLayer(layer);
                            this.almacenamientoTarea['geojsonsubconjunto'] = JSON.stringify(layer.toGeoJSON());
                        }
                    });

                    taskMap.on(L.Draw.Event.DELETED, (e) => {

                        this.almacenamientoTarea.geojsonsubconjunto = null;
                    });
                }

                this.taskMap = taskMap;
            }, timeout);
        },
        restablecerMapa(){
            this.taskMap.remove();
            this.generarMapa(0);
            this.almacenamientoTarea.geojsonsubconjunto = null;
        },
        cantidadAreasMapa(editableLayers){

            return Object.keys(editableLayers._layers).length;
        },
        obtenerCoordenadas(geojson){

            coordenadas = [];

            coordenadasGeojson = JSON.parse(geojson).geometry.coordinates[0];

            for(let i=0; i < coordenadasGeojson.length; i++){

                coordenadas.push(coordenadasGeojson[i].reverse())
            }

            return coordenadas;
        },
        generarDimensionTerritorial(dimension){
            if(this.almacenamientoTarea.taretipo == "1"){

                this.almacenamientoTarea.dimensionIDparaTerritorialD = dimension.dimension_id
                this.taskMap.remove();
                this.almacenamientoTarea.geojsonsubconjunto = null;
                this.generarMapa(0, dimension);
            }
        },
        generarDimensionTerritorialCampana(dimension){
            if(this.almacenamientoTarea.task_type_id == "1"){

                this.almacenamientoTarea.dimensionIDparaTerritorialD = dimension.dimension_id
                this.taskMap.remove();
                this.almacenamientoTarea.geojsonsubconjunto = null;
                this.generarMapa(0, dimension);
            }
        },
        validarSubconjunto(geojson){

            coordsFails = 0;

            var polyPoints = this.dimensionTerritorialReferencia.getLatLngs()[0];

            coordenadas = this.obtenerCoordenadas(JSON.stringify(geojson));

            for(var k = 0; k < coordenadas.length; k++){

                var x = coordenadas[k][0], y = coordenadas[k][1];

                var inside = false;
                for (var i = 0, j = polyPoints.length - 1; i < polyPoints.length; j = i++) {
                    var xi = polyPoints[i].lat, yi = polyPoints[i].lng;
                    var xj = polyPoints[j].lat, yj = polyPoints[j].lng;

                    var intersect = ((yi > y) != (yj > y))  && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
                    if (intersect) inside = !inside;
                }

                if(!inside){
                    coordsFails++
                };
            }

            if(coordsFails > 0){

                return false;

            } else{

                return true;
            }
        },
        generarDimensionTerritorialInstrumento(instrumento){

            if(this.almacenamientoTarea.taretipo == "2"){

                this.taskMap.remove();
                this.almacenamientoTarea.geojsonsubconjunto = null;
                this.generarMapa(0, instrumento);
            }
        },
        formateoFechaInicio(date){
            this.almacenamientoTarea.tarfechainicio = moment(date).format('YYYY-MM-DD');
        },
        formateoFechaFin(date){
            this.almacenamientoTarea.tarfechacierre = moment(date).format('YYYY-MM-DD');
        },
        edicionformateoFechaInicio(date){
            this.edicionTarea.tarfechainicio = moment(date).format('YYYY-MM-DD');
        },
        edicionformateoFechaFin(date){
            this.edicionTarea.tarfechacierre = moment(date).format('YYYY-MM-DD');
        }
    },
    filters: {
        tipoTarea(value){

            if(value == 1){

                return "Encuesta";

            } else if(value == 2){

                return "Cartografia";
            }
        },
        prioridadTarea(value){

            switch(value){

                case 1:
                    response = "Alta";
                    break;
                 case 2:
                    response = "Media";
                    break;
                 case 3:
                    response = "Baja";
                    break;
            }

            return response;
        }
    },
    computed: {
        filteredTasks: function(){

          var filtro = this.filtro && this.filtro.toLowerCase()
          var tareas = this.tareas;
          if (filtro) {
            tareas = tareas.filter(function (row) {
              return Object.keys(row).some(function (key) {
                return String(row[key]).toLowerCase().indexOf(filtro) > -1
              });
            });
          }
          return tareas;
        }
    }
});