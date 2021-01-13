let rol = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-permisos-rol',
    created(){

        if(window.location.pathname.substr(0, 16) == "/roles/permisos/"){

            this.rolID = window.location.pathname.substr(16, 36);
            this.listadoPermisos();
            this.listadoAcciones();
         }
    },
    data: {
        rolID: 0,
        permisos: [],
        almacenamientoPermiso: {},
        acciones: [],
        //edicionRol: {},
        loading: false
    },
    methods: {
        listadoPermisos(){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/funciones-rol/list/' + this.rolID,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.permisos = response.data;
                this.loader(false);
            });
        },
        almacenarPermiso(){

            this.loader(true);

            this.almacenamientoPermiso.rolid = this.rolID;
            var queryString = Object.keys(this.almacenamientoPermiso).map(key => {
                return key + '=' + this.almacenamientoPermiso[key]
            }).join('&');

            axios({
                method: 'post',
                url: '/funciones-rol/store/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-permiso").modal('hide')
                this.almacenamientoPermiso = {};
                this.listadoPermisos();

                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Permiso asignado satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(response => {

                $("#agregar-permiso").modal('hide')
                this.almacenamientoPermiso = {};

                this.loader(false);

                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        datas (ids) {
            return {
            id: ids
            }
        },
        eliminarPermiso(id, rol){

            this.rolID = rol
            
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
                    url: '/funciones-rol/delete/' + id ,
                    data: this.datas(rol),
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.listadoPermisos();

                    this.loader(false);

                    Swal.fire(
                      'Eliminado!',
                      'El permiso fue eliminado de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     this.listadoPermisos();

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
        editarRol(){

            var queryString = Object.keys(this.edicionRol).map(key => {
                return key + '=' + this.edicionRol[key];
            }).join('&');

            axios({
                method: 'post',
                url: '/roles/' + this.edicionRol.rolid,
                data: queryString,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                    $("#editar-rol").modal('hide');
                    Swal.fire(
                        'Exito!',
                        'Rol modificado satisfactoriamente',
                        'success'
                    );
                    this.listadoRoles();
            })
            .catch(() => {

                $("#editar-rol").modal('hide');

                Swal.fire(
                    'Error!',
                    'Ocurrio un error. Por favor intenta de nuevo',
                    'error'
                );
            });
        },
        listadoAcciones(){

            axios({
                method: 'GET',
                url: '/acciones/list/',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.acciones = response.data;
            });
        },
        loader(status){

            this.loading = status;
        }
    }
})