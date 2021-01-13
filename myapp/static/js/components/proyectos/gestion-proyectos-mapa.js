gestionProyecto = new Vue({
    el: '#gestion-proyectos-mapa',
    delimiters: ['[[', ']]'],
    data: {
        informacionProyecto: "",
        map: {},
        mapaProyecto: {},
        mapaTarea: {},
        proyectos: [],
        proyectoSeleccionado: {},
        proyectoGestion: {},
        tareaGestion: {},
        capaEdicion: '',
        tareaEdicion: false,
        dimensionesBarrios: [],
        barrioSeleccionadoId: '',
        edicionTarea: {},
        equiposURL: '',
        acciones: {
            objetivo: false,
            tiempo: false,
            territorio: false,
            equipo: false
        },
        gestionTerritorial: {
            areaDimensionTerritorial: true,
            listadoTareas: false,
            areaTarea: false
        },
        datosCambioTerritorial: {
            geojson: false,
            tareas: [],
            proj_id: '',
        },
        // Gestión de Equipos
        equipoProyecto: [],
        usuariosDisponiblesProyecto: [],
        // Ubicación Equipo
        equipoProyectoMapa: [],
        // Loader
        loading: false
    },
    created(){

        if(window.location.pathname == '/proyectos/gestion/'){
            this.cargarDimensionesBarrios()
            this.cargarMapa();
            this.obtenerProyectos();
            //setTimeout(() => this.ubicacionEquipoProyecto(), 1000);
        }
    },
    methods: {
        cargarMapa(layer){

            window.setTimeout(() => {

                this.map = L.map('map',  {
                    center: [3.450572, -76.538705],
                    drawControl: false,
                    zoom: 13
                });

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                }).addTo(this.map);

                L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
                  layers: 'idesc:mc_barrios',
                  format: 'image/png',
                  transparent: !0,
                  version: '1.1.0'
                }).addTo(this.map);

                if(layer){

                    L.geoJSON(layer,
                    {
                        onEachFeature: (feature, layer) => {

                            layer.on('click', () => {

                                this.capaEdicion = feature.properties;

                                if(feature.properties.type == 'dimension'){
                                    this.datosCambioTerritorial.geojson = JSON.stringify(feature)
                                    this.datosCambioTerritorial.proj_id = this.capaEdicion.id
                                    this.acciones.objetivo = false;
                                    this.acciones.tiempo = true;
                                    this.acciones.territorio = true;
                                    this.acciones.equipo = true;

                                } else if(feature.properties.type == 'tarea'){

                                    this.acciones.objetivo = true;
                                    this.acciones.tiempo = false;
                                    this.acciones.territorio = false;
                                    this.acciones.equipo = false;
                                }
                            });
                        },
                        style: (feature) => {

                            return {color: feature.properties.color}
                        }
                    })
                    .bindPopup(function (layer) {
                        return layer.feature.properties.description;
                    })
                    .addTo(this.map)
                }
            }, 1000);

        },
        cargarMapaDimensionTerritorial(){

            this.mapaProyecto = L.map('mapa-dimension-territorial',  {
                center: [3.450572, -76.538705],
                drawControl: false,
                zoom: 11
            });

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }).addTo(this.mapaProyecto);

            L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
              layers: 'idesc:mc_barrios',
              format: 'image/png',
              transparent: !0,
              version: '1.1.0'
            }).addTo(this.mapaProyecto);

            var editableLayers = new L.FeatureGroup();

            this.mapaProyecto.addLayer(editableLayers);

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

            this.mapaProyecto.addControl(drawControl);

            this.mapaProyecto.on(L.Draw.Event.CREATED, (e) => {
                type = e.layerType;
                layer = e.layer;

                if (type === 'polygon' && this.cantidadAreasMapa(editableLayers) == 0) {

                    editableLayers.addLayer(layer);

                    this.datosCambioTerritorial['geojson'] = JSON.stringify(layer.toGeoJSON());
                }
            });

            this.mapaProyecto.on(L.Draw.Event.DELETED, (e) => {

                 if(this.cantidadAreasMapa(editableLayers) == 0){

                    this.cambioTerritorial.geojson = null;
                 }
            });
        },
        cargarMapaTarea(tarea){

            this.mapaTarea = L.map('mapa-tarea',  {
                center: [3.450572, -76.538705],
                drawControl: false,
                zoom: 11
            });

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }).addTo(this.mapaTarea);

            L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
              layers: 'idesc:mc_barrios',
              format: 'image/png',
              transparent: !0,
              version: '1.1.0'
            })
            .addTo(this.mapaTarea);

            let geojson = {
                type: "FeatureCollection",
                features: [JSON.parse(this.datosCambioTerritorial.geojson)]
            }

            L.geoJSON(geojson).addTo(this.mapaTarea);

            var editableLayers = new L.FeatureGroup();

            this.mapaTarea.addLayer(editableLayers);

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

            this.mapaTarea.addControl(drawControl);

            this.mapaTarea.on(L.Draw.Event.CREATED, (e) => {
                type = e.layerType;
                layer = e.layer;

                if (type === 'polygon' && this.cantidadAreasMapa(editableLayers) == 0) {
                    geojson = this.datosCambioTerritorial.geojson
                    if(this.isMultiPolygon(geojson)){
                        geojson = this.convertMultiPolygonToPolygon(geojson)
                    }

                    if(this.validarSubconjunto(geojson, layer.toGeoJSON())){
                        editableLayers.addLayer(layer);
                        /*this.updateTaskDimension(tarea, JSON.stringify(layer.toGeoJSON())).then(resp => {
    
                            tarea['redimensionado'] = true;
                            this.tareaEdicion = true;
                        })*/
                        tarea['dimension_geojson'] = JSON.stringify(layer.toGeoJSON());
                        tarea['redimensionado'] = true;
                        this.tareaEdicion = true;
                    }
                }
            });

            this.mapaTarea.on(L.Draw.Event.DELETED, (e) => {

                 if(this.cantidadAreasMapa(editableLayers) == 0){

                    tarea['redimensionado'] = false;
                    this.tareaEdicion = false;
                 }
            });
        },
        eliminarMapa(){

            this.map.remove();
        },
        obtenerProyectos(){
            this.loader(true);
            return new Promise((resolve, reject) => {

                axios({
                url: '/proyectos/list/',
                method: 'GET',
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
                        this.loader(false);
                        resolve(this.proyectos);
                    }
                })
                .catch(() => {
                    this.loader(false);
                    Swal.fire({
                        title: 'Ha ocurrido un error',
                        text: 'No se pudo cargar los proyectos',
                        type: 'error',
                        confirmButtonText: 'Acepto',
                    });
                    reject("");
                })
            });
        },
        cargarInformacionProyecto(informacionProyecto){

            this.proyectoSeleccionado = informacionProyecto;
            this.proyectoGestion = informacionProyecto;

            if(informacionProyecto.hasOwnProperty('dimensiones_territoriales')){

                this.eliminarMapa();

                dimensiones = informacionProyecto.dimensiones_territoriales;
                cantidadDimensiones = informacionProyecto.dimensiones_territoriales.length;

                if(cantidadDimensiones > 0){

                    features = []

                    for(let i=0; i<cantidadDimensiones; i++){

                        // Añadiendo Dimensiones geográficas
                        let feature = JSON.parse(dimensiones[i].dimension_geojson)
                        feature.properties = {
                            color: '#0CBAEF',
                            description: dimensiones[i].dimension_name,
                            dimensionid: dimensiones[i].dimension_id,
                            id: this.proyectoSeleccionado.proj_id,//dimensiones[i].proyid,
                            type: 'dimension'
                        }

                        features.push(feature)

                        tareas = this.proyectoSeleccionado.tareas//dimensiones[i].tareas;
                        cantidadTareas = tareas.length//dimensiones[i].tareas.length;

                        if(cantidadTareas > 0){
                            
                            for(let j=0; j<cantidadTareas; j++){

                                let feature = JSON.parse(tareas[j].dimension_geojson)
                                feature.properties = {
                                    color: '#F4B821',
                                    description: tareas[j].task_name,
                                    id: tareas[j].task_id,
                                    type: 'tarea'
                                }

                                features.push(feature)
                            }
                        }
                    }

                    let geojson = {
                        type: "FeatureCollection",
                        features: features
                    }

                    this.cargarMapa(geojson);

                } else{

                    this.cargarMapa();
                }
            }

        },
        gestionObjetivoProyecto(){
            this.loader(true)
            axios({
                url: '/tareas/detail/' + this.capaEdicion.id,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.tareaGestion = response.data.tarea;
                    this.tareaGestion['task_id'] = this.capaEdicion.id;
                    this.tareaGestion['task_restriction_id'] = this.tareaGestion.task_restriction;
                    $("#gestion-objetivo-tarea").modal('show');
                }
            })
            .catch(() => {
                this.loader(false)
                Swal.fire({
                    title: 'Error',
                    text: 'No se puedo recuperar la información de la Tarea',
                    type: 'error'
                });
            });
        },
        edicionObjetivoTarea(){

            // Mostrar loader
            this.loader(true);

            // Añadir Metadato en la petición para notificar Cambio de objetivo
            this.tareaGestion['gestionCambio'] = true

            queryString = Object.keys(this.tareaGestion).map(key => {

                return key + '=' + this.tareaGestion[key];
            })
            .join('&');

            axios({
                url: '/tareas/gestion-cambios/' + this.tareaGestion.task_id,
                method: 'POST',
                data: queryString,
                headers: {
                 'Content-Type': 'application/x-www-form-urlencoded',
                 Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    // Ocultar Loader
                    this.loader(false);

                    $("#gestion-objetivo-tarea").modal('hide');

                    Swal.fire({
                        title: 'Exito',
                        text: 'El Objetivo y las condiciones de campaña de la tarea se cambiaron de forma satisfactoria',
                        type: 'success'
                    });
                }
            })
            .catch(() => {
                this.loader(false)
                $("#gestion-objetivo-tarea").modal('hide');

                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrio un error. Por favor intenta de nuevo.',
                    type: 'error'
                });
            });
        },
        gestionTiempoProyecto(){
            this.loader(true);
            axios({
                url: '/proyectos/detail/' + this.capaEdicion.id,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.proyectoGestion = response.data.detail.proyecto;
                    this.proyectoGestion['proj_id'] = this.capaEdicion.id;
                    $("#gestion-proyecto").modal('show');
                }
            })
            .catch(() => {
                this.loader(false)
                Swal.fire({
                    title: 'Error',
                    text: 'No se puedo recuperar la información del Proyecto',
                    type: 'error'
                });
            });
        },
        edicionTiempoProyecto(){

            // Mostrar loader
            this.loader(true);

            // Añadir Metadato en la petición para notificar Cambio de objetivo
            this.proyectoGestion['gestionCambio'] = true;

            queryString = Object.keys(this.proyectoGestion).map(key => {

                    return key + '=' + this.proyectoGestion[key];
                })
                .join('&');

            axios({
                url: '/proyectos/basic-update/' + this.proyectoGestion.proj_id,
                method: 'POST',
                data: queryString,
                headers: {
                 'Content-Type': 'application/x-www-form-urlencoded',
                 Authorization: getToken()
                }
            })
            .then(response => {

                // Ocultar Loader
                this.loader(false);

                $("#gestion-proyecto").modal('hide');

                Swal.fire({
                    title: 'Exito',
                    text: 'El Objetivo fue cambiado de forma satisfactoria',
                    type: 'success'
                });
            })
            .catch(() => {
                this.loader(false)
                $("#gestion-proyecto").modal('hide');

                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrio un error. Por favor intenta de nuevo.',
                    type: 'error'
                });
            });
        },
        gestionTerritorioProyecto(){

            this.obtenerTareasDimensionTerritorial();

            $("#gestion-territorio-proyecto").modal({
                backdrop: 'static',
                show: true
            });

           window.setTimeout(() => {
            this.cargarMapaDimensionTerritorial();
           }, 1000);
        },
        obtenerTareasDimensionTerritorial(){

            axios({
                //url: '/tareas-dimension-territorial/' + this.capaEdicion.dimensionid,
                url: '/proyectos/detail/' + this.informacionProyecto.proj_id,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let tareas = response.data.detail.tareas;

                    for(let i=0; i<tareas.length; i++){

                        tareas[i]['redimensionado'] = false;
                    }

                    this.datosCambioTerritorial.tareas = tareas;
                }
            });
        },
        edicionTerritorioProyecto(){

            // Mostrar loader
            this.loader(true);

            let tareas = this.datosCambioTerritorial.tareas;
            let cantidadTareas = tareas.length;
            tareasNoRedimensionadas = 0;

            if(cantidadTareas > 0){

                for(let i=0; i<cantidadTareas; i++){

                    if(!tareas[i].redimensionado){

                        tareasNoRedimensionadas++;
                    }
                }

                if(tareasNoRedimensionadas == 0){

                    axios({
                        url: '/proyectos/' + this.capaEdicion.dimensionid + '/cambio-territorio/',
                        method: 'POST',
                        data: JSON.stringify(this.datosCambioTerritorial),
                        headers: {
                            Authorization: getToken()
                        }
                    })
                    .then(response => {

                        this.loader(false);

                        if(response.data.code == 200 && response.data.status == 'success'){

                            this.obtenerProyectos().then(response => {

                               proyectoEdicion = response.find(element => element.proj_id == this.capaEdicion.id);

                               this.cargarInformacionProyecto(proyectoEdicion);
                               this.closeModalCambioTerritorio();

                               Swal.fire({
                                   title: 'Exito',
                                   text: 'Cambio Correcto',
                                   type: 'success'
                               });
                            });
                        }
                    })
                    .catch(() => {
                        this.loader(false)
                        Swal.fire({
                            title: 'Error',
                            text: 'Ocurrio un error. Por favor intenta de nuevo',
                            type: 'error'
                        });
                    })

                } else {
                    this.loader(false)
                    Swal.fire({
                        title: 'Error',
                        text: 'Todas las Tareas no estan redimensionadas',
                        type: 'error'
                    });
                }

            } else{
                axios({
                    url: '/proyectos/' + this.capaEdicion.dimensionid + '/cambio-territorio/',
                    method: 'POST',
                    data: JSON.stringify(this.datosCambioTerritorial),
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.loader(false);

                    if(response.data.code == 200 && response.data.status == 'success'){

                        this.obtenerProyectos().then(response => {

                           proyectoEdicion = response.find(element => element.proj_id == this.capaEdicion.id);

                           this.cargarInformacionProyecto(proyectoEdicion);
                           this.closeModalCambioTerritorio();

                           Swal.fire({
                               title: 'Exito',
                               text: 'Cambio Correcto',
                               type: 'success'
                           });
                        });
                    }
                })
                .catch(() => {
                    this.loader(false)
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrio un error. Por favor intenta de nuevo',
                        type: 'error'
                    });
                })

            }
        },
        paso2GestionTerritorial(){
            /*if(!this.datosCambioTerritorial.geojson){
                this.datosCambioTerritorial.geojson = this.informacionProyecto.dimensiones_territoriales[0].
            }*/
            this.gestionTerritorial.areaDimensionTerritorial = false;
            this.gestionTerritorial.listadoTareas = true;
            this.gestionTerritorial.areaTarea = false;

            this.tareaEdicion = false;
        },
        paso3GestionTerritorial(tarea){

            this.gestionTerritorial.areaDimensionTerritorial = false;
            this.gestionTerritorial.listadoTareas = false;
            this.gestionTerritorial.areaTarea = true;

            if(Object.keys(this.mapaTarea).length > 0){

                this.mapaTarea.remove();
            }

            window.setTimeout(() => { this.cargarMapaTarea(tarea) }, 1000);
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
        isMultiPolygon(geojson){
            geoJSON = JSON.parse(geojson);
            typeGeometry = geoJSON.geometry.type
            if(typeGeometry === "MultiPolygon"){
                return true;
            }
            return false;
        },
        convertMultiPolygonToPolygon(geojson){
            multiPolygon = JSON.parse(geojson);
            polygon = multiPolygon.geometry.coordinates[0];
            multiPolygon.geometry.type = "Polygon"
            multiPolygon.geometry.coordinates = polygon;
            return JSON.stringify(multiPolygon)
        },
        validarSubconjunto(geojson, geojsonSubset){

            coordsFails = 0;

            var polyPoints = this.obtenerCoordenadas(geojson);
            coordenadas = this.obtenerCoordenadas(JSON.stringify(geojsonSubset));

            for(var k = 0; k < coordenadas.length; k++){

                var x = coordenadas[k][0], y = coordenadas[k][1];

                var inside = false;
                for (var i = 0, j = polyPoints.length - 1; i < polyPoints.length; j = i++) {
                    var xi = polyPoints[i][0], yi = polyPoints[i][1];
                    var xj = polyPoints[j][0], yj = polyPoints[j][1];

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
        // Gestión de Equipos
        obtenerEquipoProyecto(proyid){

            axios({
                method: 'GET',
                url: '/equipos/list/' + proyid,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.equipoProyecto = response.data.equipo;
                }
            });
        },
        agregarIntegranteEquipo(userid){

            // Mostrar loader
            this.loader(true);

            let data = 'userid=' + userid + "&proyid=" +  this.capaEdicion.id;

            // Añadir Metadato en la petición para notificar Cambio de objetivo
            data += "&gestionCambio=true";

            axios({
                data: data,
                headers: {
                    'Authorization': getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                method: 'POST',
                url: '/equipos/store/'
            })
            .then(response => {

                // Ocultar Loader
                this.loader(false);

                if(response.data.code == 201 && response.data.status == 'success'){

                    this.obtenerEquipoProyecto(this.capaEdicion.id);
                    this.obtenerUsuariosDisponiblesProyecto();
                }
            })
        },
        eliminarIntegranteEquipo(equid){

            // Mostrar loader
            this.loader(true);

            // Añadir Metadato en la petición para notificar Cambio de objetivo
            data = "gestionCambio=true";

            axios({
                data: data,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                method: 'DELETE',
                url: '/equipos/delete/' + equid
            })
            .then(response => {

                // Ocultar Loader
                this.loader(false);

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.obtenerEquipoProyecto(this.capaEdicion.id);
                    this.obtenerUsuariosDisponiblesProyecto();
                }
            });
        },
        obtenerUsuariosDisponiblesProyecto(proyid){

            axios({
                headers:{
                    Authorization: getToken()
                },
                method: 'GET',
                url: '/equipos/' + this.capaEdicion.id + '/usuarios-disponibles/'
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.usuariosDisponiblesProyecto = response.data.usuarios;
                }
            });
        },
        gestionEquipoProyecto(){
            this.equiposURL = "/equipos/proyecto/"+this.capaEdicion.id//0eb624c4-2627-4067-8a04-38b13cc21ced"
            //this.obtenerEquipoProyecto(this.capaEdicion.id);
            //this.obtenerUsuariosDisponiblesProyecto(this.capaEdicion.id);

            $("#gestion-equipo-proyecto").modal({
                backdrop: 'static',
                show: true,
            });
        },
        ubicacionEquipoProyecto(){

            // Cantidad de capas en el mapa
            capasMapa =  Object.keys(this.map._layers)

            // Contador de features para el mapa
            cantidadFeaturesMapa = 0;

            // Calculo de features para el mapa
            for(let i=0; i<capasMapa.length; i++){

                if(this.map._layers[capasMapa[i]].hasOwnProperty('feature')){

                    cantidadFeaturesMapa++;
                }
            }

            // Consulta de ubicación para el equipo del proyecto seleccionado
            if(cantidadFeaturesMapa > 0){

                axios({
                    headers: {
                        Authorization: getToken()
                    },
                    method: 'GET',
                    url: '/equipos/list/' + this.proyectoSeleccionado.proyid
                })
                .then(response => {

                    // Eliminación de Marcadores de Equipo de Proyecto
                    for(let i=0; i<this.equipoProyectoMapa.length; i++){

                        this.equipoProyectoMapa[i].remove();
                    }

                    this.equipoProyectoMapa = [];

                    if(response.data.code == 200 && response.data.status == 'success'){

                        let equipo = response.data.equipo;

                        if(equipo.length > 0){

                            for(let i=0; i<equipo.length; i++){

                                if(equipo[i].latitud && equipo[i].longitud){

                                    marcador = L.marker([
                                            parseFloat(equipo[i].latitud),
                                            parseFloat(equipo[i].longitud)
                                        ], {title: equipo[i].userfullname}
                                    )
                                    .addTo(this.map);

                                    this.equipoProyectoMapa.push(marcador);
                                }
                            }
                        }

                        setTimeout(() => this.ubicacionEquipoProyecto(), 30000);
                    }

                })

            } else{

                setTimeout(() => this.ubicacionEquipoProyecto(), 5000);
            }
        },
        updateTaskDimension(tarea, geojson){
            return new Promise((resolve, reject) => {
                data = {
                    geojson: geojson
                }
                let queryString = Object.keys(data).map(key => {

                    return key + '=' + data[key]
                })
                .join('&')
                axios({
                    url: 'dimensiones/'+tarea.territorial_dimension_id+'/geojson/',
                    method: 'POST',
                    data: queryString,
                    headers: {
                        'Content-type': 'application/x-www-form-urlencoded',
                        Authorization: getToken()
                    }
                }).then(response => {
                    this.loader(false)
                    Swal.fire({
                        title: '¡Éxito!',
                        text: 'La dimensión de la tarea se actualizó exitosamente.',
                        type: 'success',
                        confirmButtonText: 'Aceptar',
                    });
                    resolve(response.data)

                }).catch(()=> {
                    this.loader(false)
                    Swal.fire({
                        title: 'Ha ocurrido un error',
                        text: 'No se pudo actualizar la dimensión de la tarea.',
                        type: 'error',
                        confirmButtonText: 'Aceptar',
                    });
                    reject("");
                })
            })

        },
        cargarDimensionesBarrios(){
            axios({
                url: '/dimensiones/barrios/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            }).then(response => {
                this.dimensionesBarrios = response.data
            }).catch(()=> {
                console.error("error al cargar dimensiones barrios")
            })
        },
        cargarDimensionBarrio(dimensionid){
            this.loader(true)
            axios({
                url: '/dimensiones/'+dimensionid,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            }).then(response => {
                this.cargarPoligonoPrecargado(response.data)
                this.loader(false)
            }).catch(()=> {
                this.loader(false)
                console.error("error al cargar dimension del barrio")
            })
        },
        cargarPoligonoPrecargado(dimension){
            this.mapaProyecto.remove()
            this.cargarMapaDimensionTerritorial()
            feature_proj = JSON.parse(dimension.fields.dimension_geojson)
            this.datosCambioTerritorial.geojson = dimension.fields.dimension_geojson
            feature_proj.properties = {
                color: '#0CBAEF',
                description: dimension.fields.dimension_name,
                id: dimension.pk,
                type: 'dimension'
            }
            let geojson = {
                type: "FeatureCollection",
                features: [feature_proj]
            }
            window.setTimeout(() => {

                if(geojson){
                    L.geoJSON(geojson,
                    {
                        style: (feature) => {
                            return {color: feature.properties.color}
                        }
                    })
                    .bindPopup(function (layer) {
                        return layer.feature.properties.description;
                    })
                    .addTo(this.mapaProyecto)
                }
            }, 500);
        },
        edicionformateoFechaInicio(date){
            this.edicionTarea.tarfechainicio = moment(date).format('YYYY-MM-DD');
        },
        edicionformateoFechaFin(date){
            this.edicionTarea.tarfechacierre = moment(date).format('YYYY-MM-DD');
        },
        closeModalCambioTerritorio(){
            $("#gestion-territorio-proyecto").modal('hide');
            this.datosCambioTerritorial.geojson = false
            this.datosCambioTerritorial.tareas = []
            this.acciones = {
              objetivo: false,
              territorio: false,
              tiempo: false
            }

            this.gestionTerritorial = {
              areaDimensionTerritorial: true,
              areaTarea: false,
              listadoTareas: false
            }
        },
        loader(status){

            this.loading = status;
        }
    }
});