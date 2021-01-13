let decision = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-decisiones',
    created(){
        if(window.location.pathname == '/decisiones/'){

            this.listadoDecisiones();
            this.listadoUsuarios();
        }
    },
    data: {
        decisiones: [],
        edicionDecision: {},
        almacenamientoDecision: {},
        usuarios: [],
        loading: false,
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        // Busqueda
        filter: '',
        // Campos Decision
        decisionesFields: [
            {
                label: 'Nombre',
                key: 'decs_name',
                sortable: true
            },
            {
                label: 'Descripcion',
                key: 'decs_description',
                sortable: true
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    methods: {
        listadoDecisiones(){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/decisiones/list/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.decisiones = response.data;
                this.loader(false);
            });
        },
        almacenarDecision(){

            this.loader(true);

            //this.almacenamientoDecision.userid = getUser().userid;

            var queryString = Object.keys(this.almacenamientoDecision).map(key => {
                return key + '=' + this.almacenamientoDecision[key]
            }).join('&');
            axios({
                method: 'post',
                url: '/decisiones/store/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-decision").modal('hide')
                this.almacenamientoDecision = {};
                this.listadoDecisiones();

                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Decisión creada satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(response => {

                $("#agregar-decision").modal('hide')
                this.almacenamientoDecision = {};

                this.loader(false);

                Swal.fire({
                  title: 'Error!',
                  text: 'Ya existe una decisión con el nombre digitado, verifica la información',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        eliminarDecision(id){

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
                    url: '/decisiones/delete/' + id,
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.listadoDecisiones();
                    this.loader(false);

                    Swal.fire(
                      'Eliminado!',
                      'La decision fue eliminada de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     this.listadoDecisiones();
                     this.loader(false);

                     Swal.fire(
                      'Error!',
                      'No es posible eliminar la decisión debido a que está vinculada a un proyecto',
                      'error'
                    );
                });
              }
            });
        },
        editarDecision(){

            this.loader(true);

            var queryString = Object.keys(this.edicionDecision).map(key => {
                return key + '=' + this.edicionDecision[key];
            }).join('&');
            axios({
                method: 'post',
                url: '/decisiones/' + this.edicionDecision.decs_id,
                data: queryString,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.listadoDecisiones();
                $("#editar-decision").modal('hide');
                this.loader(false);

                Swal.fire(
                    'Exito!',
                    'Decisión modificada satisfactoriamente',
                    'success'
                );
            })
            .catch(() => {

                $("#editar-decision").modal('hide');
                this.loader(false);

                Swal.fire(
                    'Error!',
                    'Ya existe una decisión con el nombre digitado, verifica la información',
                    'error'
                );
            });
        },
        listadoUsuarios(){

            axios({
                method: 'GET',
                url: '/usuarios/list/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.usuarios = response.data;
            });
        },
        loader(status){

            this.loading = status;
        }
    },
    computed: {
        filteredDesitions(){

            var filter = this.filter && this.filter.toLowerCase();
            var decisiones = this.decisiones;

            if(filter){

                decisiones = decisiones.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1
                    });
                });
            }

            return decisiones;
        }
    }
})