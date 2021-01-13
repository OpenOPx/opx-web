miembrosPlantilla = new Vue({
    el: '#gestion-miembros-plantilla',
    delimiters: ['[[', ']]'],
    data: {
        plantillaID: '',
        miembrosPlantilla: [],
        usuariosDisponibles: [],
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'pers_name'
            },
            {
                label: 'Apellido',
                key: 'pers_lastname'
            },
            {
                label: 'Barrio',
                key: 'neighb_name'
            },
            {
                label: 'Puntaje',
                key: 'pers_score'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        // Paginación Equipo
        paginationTeam: {
            currentPage: 1,
            perPage: 10
        },
        // Búsqueda Equipo
        filterTeam: '',
        // Campos usuarios Disponibles
        availableUserFields: [
            {
                label: 'Nombre',
                key: 'pers_name'
            },
            {
                label: 'Apellido',
                key: 'pers_lastname'
            },
            {
                label: 'Barrio',
                key: 'neighb_name'
            },
            {
                label: 'Puntaje',
                key: 'pers_score'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        paginationAvailableUsers: {
            currentPage: 1,
            perPage: 10
        },
        // Busqueda usuarios disponibles
        filterAvailableUsers: '',
        loading: false
    },
    created(){
        window.setTimeout(() => {
            if(window.location.pathname.substr(1, 7) == "equipos" && window.location.pathname.substr(46, 8) == "miembros"){
                this.plantillaID = window.location.pathname.substr(9, 36);
                this.listadoMiembros();
                this.listadoUsuariosDisponibles();
            }

        }, 1000);
    },
    methods: {
        listadoMiembros(){
            axios({
                url: '/miembros-plantilla/' + window.location.pathname.substr(9, 36) + '/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.miembrosPlantilla = response.data.data;
                }
            });
        },
        listadoUsuariosDisponibles(){
            this.loader(true)
            axios({
                url: '/miembros-plantilla/' + window.location.pathname.substr(9, 36) + '/usuarios-disponibles/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.usuariosDisponibles = response.data.data;
                }
            }).catch(()=>{
                this.loader(false)
            });
        },
        agregarIntegrante(userid){
            this.loader(true)
            axios({
                url: '/miembros-plantilla/' + window.location.pathname.substr(9, 36) + '/store/',
                method: 'POST',
                data: 'usuarioId=' + userid,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
                this.loader(false)
                if(response.data.code == 201 && response.data.status == 'success'){

                    this.listadoMiembros();
                    this.listadoUsuariosDisponibles();
                }
            }).catch(()=> {
                this.loader(false)
            });
        },
        eliminarIntegrante(miplid){

            Swal.fire({
                text: '¿Estas seguro?',
                showCancelButton: true
            })
            .then(result => {

                if(result.value){
                    this.loader(true)
                     axios({
                        url: '/miembros-plantilla/' + miplid + '/delete/',
                        method: 'DELETE',
                        headers: {
                            Authorization: getToken()
                        }
                    })
                    .then(response => {
                        this.loader(false)
                        if(response.data.code == 200 && response.data.status == 'success'){

                            this.listadoMiembros();
                            this.listadoUsuariosDisponibles();

                            Swal.fire(
                                'Exito',
                                'Miembro Eliminado correctamente del equipo',
                                'success'
                            )
                        }
                    }).catch(()=>{
                        this.loader(false)
                    })
                }
            });
        },
        loader(status){
            this.loading = status;
        }
    },
    computed: {
        filteredTeam(){

            var filter = this.filterTeam && this.filterTeam.toLowerCase();
            var miembrosPlantilla = this.miembrosPlantilla;

            if(filter){

                miembrosPlantilla = miembrosPlantilla.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return miembrosPlantilla;
        },
        filteredAvailableUsers(){

            var filter = this.filterAvailableUsers && this.filterAvailableUsers.toLowerCase();
            var usuariosDisponibles = this.usuariosDisponibles;

            if(filter){

                usuariosDisponibles = usuariosDisponibles.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return usuariosDisponibles;
        }
    }
})