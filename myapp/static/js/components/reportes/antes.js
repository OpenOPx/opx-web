estadisticas = new Vue({
    el: '#dashboard',
    delimiters: ['[[', ']]'],
    created(){

        if(window.location.pathname == '/reportes/antes/'){

           this.obtenerDatosGenerales();
           this.obtenerInfoEquipos();
           this.obtenerRanking();
           this.usuariosXRol();
           this.usuariosXGenero();
           this.tareasPorTipo();
           this.usuariosXBarrio();
           this.usuariosXNivelEducativo();
           this.listadoProyectos();
        }
    },
    data: {

        datosGenerales: 0,
        ranking: [],
        infoEquipos:[]

    },
    methods: {
        obtenerDatosGenerales(){

            axios({
                url: '/estadisticas/datos-generales/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.datosGenerales = response.data.data;
            })
        },
        obtenerInfoEquipos(){
          console.log("INICIOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

          axios({
              url: 'plantillas-equipo/list/',
              method: 'GET',
              headers: {
                  Authorization: getToken()
              }
          })
          .then(response => {

              if(response.data.code == 200 && response.data.status == 'success'){
                  this.infoEquipos = response.data.data;
                  console.log("BUENA CONSULTAAAAAAAAAAAAAAAAAAAAAA")
              }else{
                  console.log("RESPONSE DATA: "+response.data.data)
              }
          });
      },
        usuariosXRol(){

            axios({
                url: '/estadisticas/usuarios-x-rol/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                let data = response.data.data;

                let ctx = document.getElementById("usuarios-rol").getContext('2d')
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                      labels: data.roles,
                      datasets: [
                        {
                          label: "Usuarios x Rol",
                          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                          data: data.cantidadUsuarios
                        }
                      ]
                    },
                    options: {
                      title: {
                        display: true,
                        text: 'Usuarios x Rol'
                      }
                    }
                });
            })


        },
        usuariosXGenero(){

            axios({
                url: '/estadisticas/usuarios-x-genero/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let data = response.data.data;
                    let ctx = document.getElementById("usuarios-genero").getContext('2d')

                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                          labels: data.generos,
                          datasets: [
                            {
                              label: "Usuarios x Género",
                              backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                              data: data.cantidad
                            }
                          ]
                        },
                        options: {
                          title: {
                            display: true,
                            text: 'Usuarios x Género'
                          }
                        }
                    });
                }
            });
        },
        tareasPorTipo(){

            axios({
                url: '/estadisticas/tareas-x-tipo/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let data = response.data.data;
                    let ctx = document.getElementById("tareas-tipo").getContext('2d')

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
            });
        },
        usuariosXBarrio(){

            axios({
                url: '/estadisticas/usuarios-x-barrio/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let data = response.data.data;
                    let ctx = document.getElementById("usuarios-barrio").getContext('2d')

                    new Chart(ctx, {
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

                }
            });
        },
        usuariosXNivelEducativo(){

            axios({
                url: '/estadisticas/usuarios-x-nivel-educativo/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let data = response.data.data;
                    let ctx = document.getElementById("usuarios-nivel-educativo").getContext('2d')

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
            });
        },
        obtenerRanking(){

            axios({
                url: '/estadisticas/ranking/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.ranking = response.data.data;
            })
        }
    }
})