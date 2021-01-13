proyecto = new Vue({
    el: '#gestion-proyectos',
    delimiters: ['[[', ']]'],
    data: {
        almacenamientoProyecto: {
            delimitacionesGeograficas: [],
            tiproid: ''
        },
        decisiones: [],
        dimensionesPre: [],
        edicionProyecto: {},
        proyectos: [],
        proyectosFields: [
            {
                label: 'Nombre',
                key: 'proj_name',
                sortable: true
            },
            {
                label: 'Descripción',
                key: 'proj_description',
                sortable: true
            },
            {
                label: 'Fecha de inicio',
                key: 'proj_start_date',
                sortable: true
            },
            {
                label: 'Fecha de cierre',
                key: 'proj_close_date',
                sortable: true
            },
            {
                label: 'Completitud (%)',
                key: 'proj_completness',
                sortable: true
            },
            {
                key: 'acciones',
                label: ''
            }
        ],
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        tiposProyecto: [],
        contextos: [],
        plantillas: [],
        loading: false,
        mapObject: {},
        delimitacionGeografica: {
            geojson: null
        },
        delimitacionGeograficaEdicion: null,
        filterKey: ''
    },
    created() {

        if (window.location.pathname == '/proyectos/') {

            this.listadoProyectos();
            this.listadoDimensionesPrecargadas();
            this.listadoDecisiones();
            this.listadoContextos();
            this.listadoPlantillas();
            this.listadoTiposProyecto();
        }
    },
    methods: {
        listadoProyectos() {

            this.loader(true);

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

                    this.loader(false);

                    if (response.data.code == 200 && response.data.status == 'success') {

                        this.proyectos = response.data.proyectos;
                    }
                });
        },
        almacenarProyecto() {
            //this.almacenamientoProyecto.proypropietario = getUser().id;

            this.loader(true);
            var queryString = Object.keys(this.almacenamientoProyecto).map(key => {

                if (key == 'dimensionesPre') {
                    let dimensionesPrec = [];

                    for (let i = 0; i < this.almacenamientoProyecto.dimensionesPre.length; i++) {
                        dimensionesPrec.push(this.almacenamientoProyecto.dimensionesPre[i].dimension_id);
                    }

                    valor = JSON.stringify(dimensionesPrec);
                } else if (key == 'decisiones') {

                    let decisiones = [];

                    for (let i = 0; i < this.almacenamientoProyecto.decisiones.length; i++) {

                        decisiones.push(this.almacenamientoProyecto.decisiones[i].decs_id);
                    }
                    valor = JSON.stringify(decisiones);
                } else if (key == 'contextos') {

                    let contextos = [];

                    for (let i = 0; i < this.almacenamientoProyecto.contextos.length; i++) {


                        contextos.push(this.almacenamientoProyecto.contextos[i].context_id);
                    }

                    valor = JSON.stringify(contextos);
                } else if (key == 'plantillas') {

                    let plantillas = [];

                    for (let i = 0; i < this.almacenamientoProyecto.plantillas.length; i++) {


                        plantillas.push(this.almacenamientoProyecto.plantillas[i].team_id);
                    }

                    valor = JSON.stringify(plantillas);
                } else if (key == 'delimitacionesGeograficas') {

                    valor = JSON.stringify(this.almacenamientoProyecto.delimitacionesGeograficas);
                } else {

                    valor = this.almacenamientoProyecto[key]
                }
                return key + '=' + valor
            }).join('&');
            axios({
                method: 'post',
                url: '/proyectos/store/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
                .then(response => {

                    $("#agregar-proyecto").modal('hide');
                    this.almacenamientoProyecto = {
                        delimitacionesGeograficas: []
                    };
                    this.listadoProyectos();

                    this.loader(false);

                    Swal.fire({
                        title: 'Exito!',
                        text: 'Debes diligenciar todos los campos',
                        type: 'success',
                        confirmButtonText: 'Acepto'
                    });
                })
                .catch(response => {

                    $("#agregar-proyecto").modal('hide');
                    this.almacenamientoProyecto = {
                        delimitacionesGeograficas: []
                    };
                    this.almacenamientoProyecto.proyfechainicio = null;
                    this.almacenamientoProyecto.proyfechacierre = null;

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
        generarMapa(timeout, coordenadas) {

            window.setTimeout(() => {

                let mapObject = L.map('dimension').setView([3.450572, -76.538705], 13);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                }).addTo(mapObject);

                L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
                    layers: 'idesc:mc_barrios',
                    format: 'image/png',
                    transparent: !0,
                    version: '1.1.0'
                }).addTo(mapObject);

                var editableLayers = new L.FeatureGroup();

                mapObject.addLayer(editableLayers);

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

                mapObject.addControl(drawControl);

                mapObject.on(L.Draw.Event.CREATED, (e) => {
                    type = e.layerType;
                    layer = e.layer;

                    if (type === 'polygon' && this.cantidadAreasMapa(editableLayers) == 0) {

                        editableLayers.addLayer(layer);

                        this.delimitacionGeografica['geojson'] = JSON.stringify(layer.toGeoJSON());
                    }
                });

                mapObject.on(L.Draw.Event.DELETED, (e) => {

                    if (this.cantidadAreasMapa(editableLayers) == 0) {

                        this.delimitacionGeografica.geojson = null;
                    }
                });

                if (coordenadas) {

                    L.polygon(coordenadas).addTo(mapObject);
                }

                this.mapObject = mapObject;

            }, timeout);
        },
        cantidadAreasMapa(editableLayers) {

            return Object.keys(editableLayers._layers).length;
        },
        restablecerMapa() {

            this.mapObject.remove();
            this.generarMapa(0);
        },
        restablecerDelimitacionGeografica() {

            this.delimitacionGeografica = {
                nombre: null,
                geojson: null
            }

            this.delimitacionGeograficaEdicion = null;
        },
        agregarDelimitacionGeografica() {

            this.almacenamientoProyecto.delimitacionesGeograficas.push(this.delimitacionGeografica);

            this.restablecerDelimitacionGeografica();
            this.restablecerMapa();
        },
        eliminarDelimitacionGeografica(index) {

            Swal.fire({
                title: 'Estas seguro?',
                text: 'Estas seguro que deseas eliminar esta dimensión?. Es irreversible',
                type: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Acepto!'
            })
                .then(result => {

                    if (result.value) {
                        this.almacenamientoProyecto.delimitacionesGeograficas.splice(index, 1);
                    }
                });
        },
        detalleDelimitacionGeografica(delimitacion, index) {
            this.delimitacionGeografica = delimitacion;
            this.delimitacionGeograficaEdicion = index.toString();

            coordenadasLeaflet = JSON.parse(delimitacion.geojson)['geometry']['coordinates'][0];
            coordenadas = []

            for (let i = 0; i < coordenadasLeaflet.length; i++) {

                coordenadas.push(coordenadasLeaflet[i].reverse());
            }

            this.mapObject.remove();
            this.generarMapa(0, coordenadas);
        },
        actualizarDelimitacionGeografica() {

            this.almacenamientoProyecto.delimitacionesGeograficas[parseInt(this.delimitacionGeograficaEdicion, 10)] = this.delimitacionGeografica;

            this.restablecerMapa();
            this.restablecerDelimitacionGeografica();
        },
        eliminarProyecto(id) {

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
                        method: 'delete',
                        url: '/proyectos/delete/' + id,
                        headers: {
                            Authorization: getToken()
                        }
                    })
                        .then(response => {

                            this.listadoProyectos();

                            this.loader(true);

                            Swal.fire(
                                'Eliminado!',
                                'El proyecto fue eliminado de forma exitosa',
                                'success'
                            );
                        })
                        .catch(response => {

                            this.listadoProyectos();

                            this.loader(false);

                            Swal.fire(
                                'Error!',
                                'No es posible eliminar el proyecto debido a que tiene tareas vinculadas',
                                'error'
                            );
                        });
                }
            });
        },
        editarProyecto() {

            this.loader(true);

            var queryString = Object.keys(this.edicionProyecto).map(key => {

                if (key == 'dimensionesPre') {
                    let dimensionesPrec = [];

                    for (let i = 0; i < this.almacenamientoProyecto.dimensionesPre.length; i++) {
                        dimensionesPrec.push(this.almacenamientoProyecto.dimensionesPre[i].dimension_id);
                    }

                    valor = JSON.stringify(dimensionesPrec);
                } else if (key == 'decisiones') {

                    let decisiones = [];

                    for (let i = 0; i < this.edicionProyecto.decisiones.length; i++) {

                        decisiones.push(this.edicionProyecto.decisiones[i].decs_id);
                    }
                    valor = JSON.stringify(decisiones);

                } else if (key == 'contextos') {

                    let contextos = [];

                    for (let i = 0; i < this.edicionProyecto.contextos.length; i++) {


                        contextos.push(this.edicionProyecto.contextos[i].context_id);
                    }

                    valor = JSON.stringify(contextos);

                } else {

                    valor = this.edicionProyecto[key]
                }

                return key + '=' + valor
            }).join('&');

            axios({
                method: 'post',
                url: '/proyectos/' + this.edicionProyecto.proj_id,
                data: queryString,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
                .then(response => {

                    this.listadoProyectos();
                    $("#editar-proyecto").modal('hide');
                    this.loader(false);

                    Swal.fire(
                        'Exito!',
                        'Proyecto modificado satisfactoriamente',
                        'success'
                    );
                })
                .catch(() => {

                    $("#editar-proyecto").modal('hide');
                    this.loader(false);

                    Swal.fire(
                        'Error!',
                        'Ocurrio un error. Por favor intenta de nuevo',
                        'error'
                    );
                })
        },
        listadoDecisiones() {

            axios({
                method: 'GET',
                url: '/decisiones/list/',
                headers: {
                    Authorization: getToken()
                }
            })
                .then(response => {
                    this.decisiones = response.data;
                })
        },
        listadoDimensionesPrecargadas() {
            axios({
                method: 'GET',
                url: '/dimensionesPre/',
                headers: {
                    Authorization: getToken()
                }
            })
                .then(response => {
                    this.dimensionesPre = response.data;
                })
        },
        pintarDimensionesSeleccion() {
            this.loader(true);
            let arr = [];
            for (let index = 0; index < this.almacenamientoProyecto.dimensionesPre.length; index++) {
                arr.push(this.almacenamientoProyecto.dimensionesPre[index].dimension_id);
            }

            data= {
                dimensiones_id: arr
            }
            axios({
                method: 'POST',
                url: 'dimensionesPre/mapa/',
                data: data,
                headers: {
                    Authorization: getToken()
                }
            })
                .then(response => {
                    this.ajusteGeoJson(response.data.geo)
                    this.loader(false);
                }).catch( ()=>{
                    this.loader(false);
                    Swal.fire({
                        title: 'Error!',
                        text: 'Ocurrio un error. Por favor intenta de nuevo',
                        type: 'error',
                        confirmButtonText: 'Acepto'
                    });
                } )
        },
        ajusteGeoJson(dimensiones){
            features = []

                for(let i=0; i<dimensiones.length; i++){
                    // Añadiendo Dimensiones geográficas
                    let feature = JSON.parse(dimensiones[i].fields.dimension_geojson)

                    feature.properties = {
                        color: '#3cba9f',
                        description: dimensiones[i].fields.dimension_name,
                        id: dimensiones[i].pk,
                        type: 'dimension'
                    }
                    features.push(feature)
                }

                let geojson = {
                    type: "FeatureCollection",
                    features: features
                }

                this.cargarMapa(geojson);

        },
        cargarMapa(layer){

            //this.restablecerMapa();
            window.setTimeout(() => {

                if(layer){
                    L.geoJSON(layer,
                    {
                        style: (feature) => {
                            return {color: feature.properties.color}
                        }
                    })
                    .bindPopup(function (layer) {
                        return layer.feature.properties.description;
                    })
                    .addTo(this.mapObject)
                }
            }, 1000);

        },
        listadoContextos() {
    
            axios({
                method: 'GET',
                url: '/contextos/list/',
                headers: {
                    Authorization: getToken()
                }
            })
                .then(response => {
    
                    this.contextos = response.data;
                });
        },
        listadoTiposProyecto() {
    
            axios({
                url: '/tipos-proyecto/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
                .then(response => {
    
                    if (response.data.code == 200 && response.data.status == 'success') {
    
                        this.tiposProyecto = response.data.data;
                    }
                })
        },
        loader(status) {
    
            this.loading = status;
        },
        listadoPlantillas() {
    
            axios({
                url: '/plantillas-equipo/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
                .then(response => {
    
                    if (response.data.code == 200 && response.data.status == 'success') {
    
                        this.plantillas = response.data.data;
                    }
                })
        },
        formateoFechaInicio(date) {
            this.almacenamientoProyecto.proyfechainicio = moment(date).format('YYYY-MM-DD');
        },
        formateoFechaFin(date) {
            this.almacenamientoProyecto.proyfechacierre = moment(date).format('YYYY-MM-DD');
        }
    },
    computed: {
    filteredProjects: function () {
        var filterKey = this.filterKey && this.filterKey.toLowerCase()
        var proyectos = this.proyectos
        if (filterKey) {
            proyectos = proyectos.filter(function (row) {
                return Object.keys(row).some(function (key) {
                    return String(row[key]).toLowerCase().indexOf(filterKey) > -1
                })
            })
        }
        return proyectos;
    }
}});
