let contexto = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-contextos',
    created(){
        if(window.location.pathname == '/contextos/'){

            this.listadoContextos();
        }
    },
    data: {
        contextos: [],
        edicionContexto: {},
        almacenamientoContexto: {},
        loading: false,
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        // Busqueda
        filter: '',
        // Campos Contextos
        contextsFields: [
            {
                label: 'Descripción',
                key: 'context_description',
                sortable: true
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    methods: {
        listadoContextos(){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/contextos/list/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.contextos = response.data;
                this.loader(false);
            });
        },
        almacenarContexto(){

            this.loader(true);

            var queryString = Object.keys(this.almacenamientoContexto).map(key => {
                return key + '=' + this.almacenamientoContexto[key]
            }).join('&');

            axios({
                method: 'post',
                url: '/contextos/store/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-contexto").modal('hide');
                this.almacenamientoContexto = {};
                this.listadoContextos();

                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Contexto creado satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(response => {

                $("#agregar-contexto").modal('hide')
                this.almacenamientoContexto = {};

                this.loader(false);

                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        eliminarContexto(id){

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
                    url: '/contextos/delete/' + id,
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.listadoContextos();
                    this.loader(false);

                    Swal.fire(
                      'Eliminado!',
                      'El contexto fue eliminado de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     this.listadoContextos();
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
        editarContexto(){

            this.loader(true);

            var queryString = Object.keys(this.edicionContexto).map(key => {
                return key + '=' + this.edicionContexto[key];
            }).join('&');

            axios({
                method: 'post',
                url: '/contextos/' + this.edicionContexto.contextoid,
                data: queryString,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.listadoContextos();
                $("#editar-contexto").modal('hide');
                this.loader(false);

                Swal.fire(
                    'Exito!',
                    'Contexto modificado satisfactoriamente',
                    'success'
                );
            })
            .catch(() => {

                $("#editar-contexto").modal('hide');
                this.loader(false);

                Swal.fire(
                    'Error!',
                    'Ocurrio un error. Por favor intenta de nuevo',
                    'error'
                );
            });
        },
        loader(status){

            this.loading = status;
        }
    },
    computed: {
        filteredContexts(){

            var filter = this.filter && this.filter.toLowerCase();
            var contextos = this.contextos;

            if(filter){

                contextos = contextos.filter((row) => {

                    return Object.keys(row).some((key) => {

                       return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return contextos;
        }
    }
})