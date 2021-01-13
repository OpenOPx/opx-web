let usuario = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-usuarios',
    created(){

        if(window.location.pathname == '/usuarios/'){

            this.listadoUsuarios();
            this.listadoRoles();
            this.listadoGeneros();
            this.listadoBarrios();
            this.listadoNivelesEducativos();
        }
    },
    data: {
        usuarios: [],
        edicionUsuario: {},
        almacenamientoUsuario: {},
        roles: [],
        loading: false,
        generos: [],
        barrios: [],
        nivelesEducativos: [],
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        // Filtro por estado
        activePersons: true,
        inactivePersons: false,
        // Búsqueda
        filter: '',
        // Campos Usuario
        userFields: [
            {
                label: 'Estado',
                key: 'isactive'
            },
            {
                label: 'Nombres',
                key: 'pers_name'
            },
            {
                label: 'Apellidos',
                key: 'pers_lastname'
            },
            {
                label: 'E-mail',
                key: 'useremail'
            },
            {
                label: 'Rol',
                key: 'role_name'
            },
            {
                label: 'Fecha de Creación',
                key: 'pers_creation_date'
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    methods: {
        listadoUsuarios(){

            this.loader(true);
            url_req = '/usuarios/list/';
            if(this.activePersons && this.inactivePersons){
                url_req = '/usuarios/list/?isactive=all';
            }
            else if(this.inactivePersons){
                url_req = '/usuarios/list/?isactive=inactive';
            }
            else if(!this.activePersons&&!this.inactivePersons){
                url_req = '/usuarios/list/?isactive=none';
            }
            //let users = []
            axios({
                method: 'GET',
                url: url_req,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.usuarios = response.data;
                this.loader(false);
            })
            .catch(err => {

                this.loader(false);

                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo ',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        almacenarUsuario(){

            this.loader(true);

            var queryString = Object.keys(this.almacenamientoUsuario).map(key => {
                return key + '=' + this.almacenamientoUsuario[key]
            }).join('&');

            axios({
                method: 'post',
                url: '/usuarios/store/',
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-usuario").modal('hide')
                this.almacenamientoUsuario = {};
                this.listadoUsuarios();

                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Usuario creado satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(err => {

                $("#agregar-usuario").modal('hide')
                this.almacenamientoUsuario = {};

                this.loader(false);

                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        eliminarUsuario(id){

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
                    method: "DELETE",
                    url: '/usuarios/delete/' + id,
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.listadoUsuarios();

                    this.loader(false);

                    Swal.fire(
                      'Eliminado!',
                      'El usuario fue eliminado de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     this.listadoUsuarios();

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
        editarUsuario(){

            this.loader(true);

            var queryString = Object.keys(this.edicionUsuario).map(key => {
                return key + '=' + this.edicionUsuario[key];
            }).join('&');

            axios({
                method: 'post',
                url: '/usuarios/' + this.edicionUsuario.user_id,
                data: queryString,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                    $("#editar-usuario").modal('hide');

                    this.listadoUsuarios();

                    this.loader(false);

                    Swal.fire(
                        'Exito!',
                        'Usuario modificado satisfactoriamente',
                        'success'
                    );
            })
            .catch(() => {

                $("#editar-usuario").modal('hide');

                this.loader(false);

                Swal.fire(
                    'Error!',
                    'Ocurrio un error. Por favor intenta de nuevo',
                    'error'
                );
            });
        },
        listadoRoles(){

            axios({
                method: 'GET',
                url: '/roles/list/',
                headers: {
                    Authorization: getToken()
                }
            }).then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.roles = response.data.roles;
                }
            });
        },
        listadoGeneros(){

            axios.get('/generos/list/')
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.generos = response.data.generos;
                }
            });
        },
        listadoBarrios(){

            axios.get('/barrios/list/')
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.barrios = response.data.barrios;
                }
            });
        },
        listadoNivelesEducativos(){

            axios.get('/niveles-educativos/list/')
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.nivelesEducativos = response.data.nivelesEducativos;
                }
            });
        },
        loader(status){

            this.loading = status;
        }
    },
    filters: {
        tipoTarea(value){

            if(value == 1){

                return "Encuesta";

            } else if(value == 2){

                return "Cartografia";
            }
        }
    },
    computed: {
        usuariosActives(){
            //let foo = this.activePersons
            this.listadoUsuarios()
            return 1;
        },
        filteredUsers(){

            var filter = this.filter && this.filter.toLowerCase();
            var usuarios = this.usuarios;

            if(filter){

                usuarios = usuarios.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return usuarios;
        }
    }
});