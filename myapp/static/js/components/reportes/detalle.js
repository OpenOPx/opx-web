estadisticas = new Vue({
    el: '#reportes-detalle-proyecto',
    delimiters: ['[[', ']]'],
    data: {
        proyectoID: '',
        datosGenerales: [],
        ranking: [],
        dimensionesProyecto: [],
        tareasDimension: [],
        equipoProyecto: [],
        contextosProyecto: [],
        decisionesProyecto: [],
        usuariosBarrioEspecifico: []
    },
    created(){

        if(window.location.pathname.substr(1, 8) == "reportes" && window.location.pathname.substr(47, 7) == "detalle"){

            window.setTimeout(() => {

                this.obtenerDatosGenerales();
                this.tiposTarea();
                this.usuariosXBarrio();
                this.usuariosXNivelEducativo();
                this.usuariosXRol();
                this.usuariosXGenero();
                this.getRanking();
            }, 1000);
        }
    },
    methods:{
        tiposTarea(){
            axios({
                url: '/estadisticas/' + this.proyectoID + '/tareas-x-tipo/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let ctx = document.getElementById('tipos-tarea').getContext('2d');
                    let data = response.data.data;

                    new Chart(ctx, {
                        type: 'pie',
                        data: {
                          labels: data.tipos,
                          datasets: [
                            {
                              label: "Tareas Por Tipo",
                              backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                              data: data.cantidad
                            }
                          ]
                        },
                        options: {
                          title: {
                            display: true,
                            text: 'Tareas Por Tipo'
                          }
                        }
                    });
                }
            })
        },
        usuariosXBarrio(){
            axios({
                url: '/estadisticas/' + this.proyectoID + '/usuarios-x-barrio/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let canvas = document.getElementById('usuarios-barrio');
                    let ctx = canvas.getContext('2d');
                    let data = response.data.data;

                    var diagram = new Chart(ctx, {
                        type: 'pie',
                        data: {
                          labels: data.barrios,
                          datasets: [
                            {
                              label: "Usuarios Por Barrio",
                              backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                              data: data.cantidad
                            }
                          ]
                        },
                        options: {
                          title: {
                            display: true,
                            text: 'Usuarios Por Barrio'
                          }
                        }
                    });

                    // Consulta de Información
                    canvas.onclick = evt => {

                        let keyword = getInfoChart(diagram, evt);

                        if(keyword){

                            this.getUsuariosBarrioEspecifico(keyword)
                        }
                    };
                }
            })
        },
        usuariosXNivelEducativo(){
            axios({
                url: '/estadisticas/' + this.proyectoID + '/usuarios-x-nivel-educativo/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let ctx = document.getElementById('usuarios-nivel-educativo').getContext('2d');
                    let data = response.data.data;

                    new Chart(ctx, {
                        type: 'pie',
                        data: {
                          labels: data.niveles_educativos,
                          datasets: [
                            {
                              label: "Usuarios Por Nivel Educativo",
                              backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                              data: data.cantidad
                            }
                          ]
                        },
                        options: {
                          title: {
                            display: true,
                            text: 'Usuarios Por Nivel Educativo'
                          }
                        }
                    });
                }
            })
        },
        usuariosXRol(){
            axios({
                url: '/estadisticas/' + this.proyectoID + '/usuarios-x-rol/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let ctx = document.getElementById('usuarios-rol').getContext('2d');
                    let data = response.data.data;

                    new Chart(ctx, {
                        type: 'pie',
                        data: {
                          labels: data.roles,
                          datasets: [
                            {
                              label: "Usuarios Por Rol",
                              backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                              data: data.cantidad
                            }
                          ]
                        },
                        options: {
                          title: {
                            display: true,
                            text: 'Usuarios Por Rol'
                          }
                        }
                    });
                }
            })
        },
        usuariosXGenero(){
            axios({
                url: '/estadisticas/' + this.proyectoID + '/usuarios-x-genero/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let ctx = document.getElementById('usuarios-genero').getContext('2d');
                    let data = response.data.data;

                    new Chart(ctx, {
                        type: 'pie',
                        data: {
                          labels: data.generos,
                          datasets: [
                            {
                              label: "Usuarios Por Género",
                              backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                              data: data.cantidad
                            }
                          ]
                        },
                        options: {
                          title: {
                            display: true,
                            text: 'Usuarios Por Género'
                          }
                        }
                    });
                }
            })
        },
        obtenerDatosGenerales(){

            axios({
                url: '/estadisticas/' + this.proyectoID + '/datos-generales/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.datosGenerales = response.data.data;
                }
            });
        },
        getRanking(){

            axios({
                url: '/estadisticas/' + this.proyectoID + '/ranking/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.ranking = response.data.data;
                }
            });
        },
        getDimensionesProyecto(){

            axios({
                url: '/estadisticas/' + this.proyectoID + '/campanas/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.dimensionesProyecto = response.data.dimensiones;
                }
            });
        },
        getTareasDimension(dimensionid){

            axios({
                url: '/estadisticas/' + dimensionid + '/tareas-campana/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.tareasDimension = response.data.tareas;
                }
            });
        },
        getEquipoProyecto(){

            axios({
                url: '/equipos/list/' + this.proyectoID,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.equipoProyecto = response.data.equipo;
            })
        },
        getContextosProyecto(){

            axios({
                url: '/contextos/' + this.proyectoID + '/list/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.contextosProyecto = response.data.contextos;
                }
            });
        },
        getDecisionesProyecto(){

            axios({
                url: '/decisiones/' + this.proyectoID + '/list/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.decisionesProyecto = response.data.decisiones;
                }
            });
        },
        getUsuariosBarrioEspecifico(keyword){

            axios({
                url: '/estadisticas/' + this.proyectoID + '/usuarios-x-barrio/' + keyword,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    // Obtención de información
                    this.usuariosBarrioEspecifico = response.data.usuarios;

                    // Mostrar Modal
                    $("#usuariosBarrioEspecifico").modal('show');
                }
            });
        },
        getModalCampanas(){

            this.getDimensionesProyecto();
            $("#dimensionesProyecto").modal('show');
        },
        getModalEquipo(){

            $("#equipoProyecto").modal('show');
            this.getEquipoProyecto();
        },
        getModalContextos(){

            this.getContextosProyecto();
            $("#contextosProyecto").modal('show');
        },
        getModalDecisiones(){

            this.getDecisionesProyecto();
            $("#decisionesProyecto").modal('show');
        }
    }
})