let equipo = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-equipo',
    data: {
        equipo: [],
        usuariosDisponibles: [],
        proyectoID: '',
        loading: false,
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'team_name'
            },
            {
                label: 'Efectividad',
                key: 'team_effectiveness'
            },
            {
                label: 'Lider',
                key: 'name_owner'
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
                key: 'team_name'
            },
            {
                label: 'Efectividad',
                key: 'team_effectiveness'
            },
            {
                label: 'Lider',
                key: 'name_owner'
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
        filterAvailableUsers: ''
    },
    created(){
        if(window.location.pathname.substr(1, 16) == "equipos/proyecto"){
            this.proyectoID = window.location.pathname.substr(18);
            this.obtenerEquipos();
            this.obtenerUsuariosDisponibles();
        }
    },
    methods: {
        obtenerEquipos(){
            this.loader(true);
            axios({
                url: '/equipos/list/' + this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false);
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.equipo = response.data.equipo;

                }
            });
        },
        obtenerUsuariosDisponibles(){

            axios({
                url: '/equipos/' + this.proyectoID + "/equipos-disponibles/",
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.usuariosDisponibles = response.data.equipo;
                }
            })
        },
        addIntegrante(teamID){
            this.loader(true)
            data = "equipoId=" + teamID + "&proyectoId=" + this.proyectoID;

            axios({
                url: '/equipos/store/',
                method: 'POST',
                data: data,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)
                if(response.data.code == 201 && response.data.status == 'success'){

                    this.obtenerEquipos();
                    this.obtenerUsuariosDisponibles();
                }
            }).catch(()=> {
                this.loader(false)
            });
        },
        eliminarIntegrante(equID){
            this.loader(true)
            axios({
                url: '/equipos/delete/' + equID,
                method: 'DELETE',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.obtenerEquipos();

                    this.obtenerUsuariosDisponibles();
                }
            }).catch(()=> {
                this.loader(false)
            })
        },
        loader(status){

            this.loading = status;
        }
    },
    computed: {
        filteredTeam(){

            var filter = this.filterTeam && this.filterTeam.toLowerCase();
            var equipo = this.equipo;

            if(filter){

                equipo = equipo.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return equipo;
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