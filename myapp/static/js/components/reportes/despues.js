estadisticas = new Vue({
    el: '#reportes-despues',
    delimiters: ['[[', ']]'],
    data: {
        proyectos: [],
        vistaTarjetas: true,
        vistaGantt: false
    },
    created(){

        if(window.location.pathname == '/reportes/despues/'){

            this.listadoProyectos();
            this.listadoProyectosGantt();
        }
    },
    methods: {
        listadoProyectos(){

            axios({
                url: '/estadisticas/estado-proyectos-vencidos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.proyectos = response.data.data;
                }
            });
        },
        listadoProyectosGantt(){

            axios({
                url: '/estadisticas/proyectos-tareas-vencidos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    new Gantt('#proyectos-gantt', response.data.data, {
                        on_click: (task) => {

                            if(task.type == 'project'){

                                statsPromises = [this.tareasXTipo(task.id), this.tareasXEstado(task.id)];

                                Promise.all(statsPromises)
                                .then(() => {

                                    $("#estadisticas-tareas").modal('show');
                                })
                                .catch((reason) => {
                                    Swal.fire({
                                        title: 'Error',
                                        text: 'Ocurrio un error. Por favor intenta de nuevo',
                                        type: 'error'
                                    });
                                });
                            }
                        }
                    });
                }
            });
        },
        tareasXTipo(proyectoID){

            return new Promise((resolve,reject) => {

                axios({
                    url: '/estadisticas/' + proyectoID + '/tareas-x-tipo/',
                    method: 'GET',
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    if(response.data.code == 200 && response.data.status == 'success'){

                        let data = response.data.data;

                        let ctx = document.getElementById("tareas-x-tipo").getContext('2d')
                        new Chart(ctx, {
                            type: 'doughnut',
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

                        resolve("");

                    } else{

                        reject("");
                    }
                })
            })
        },
        tareasXEstado(proyectoID){

            return new Promise((resolve,reject) => {

                axios({
                    url: '/estadisticas/' + proyectoID + '/tareas-x-estado/',
                    method: 'GET',
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    if(response.data.code == 200 && response.data.status == 'success'){

                        let data = response.data.data;

                        let ctx = document.getElementById("tareas-x-estado").getContext('2d')
                        new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                              labels: data.estados,
                              datasets: [
                                {
                                  label: "Tareas Por Estado",
                                  backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                                  data: data.cantidad
                                }
                              ]
                            },
                            options: {
                              title: {
                                display: true,
                                text: 'Tareas Por Estado'
                              }
                            }
                        });

                        resolve("");

                    } else{

                        reject("");
                    }
                })
            });
        },
        cambioVista(vista){

            if(vista == 1){

                this.vistaTarjetas = true;
                this.vistaGantt = false;

            } else if(vista == 2){

                this.vistaTarjetas = false;
                this.vistaGantt = true;
            }
        },
        detalle(id){

            location.href = '/reportes/' + id + '/detalle/';
        }
    }
});