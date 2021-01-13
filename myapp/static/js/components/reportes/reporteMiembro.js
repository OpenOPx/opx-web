reporteMiembro = new Vue({
    el: '#reportes-individual-miembro',
    delimiters: ['[[', ']]'],
    data: {
        equipos: [],
        proyectos: [],
        personaId: '',
        persona: {},
        loading: false,
        // Campos Equipos
        teamFields: [
            {
                label: 'Nombre',
                key: 'team_name'
            },
            {
                label: 'Nombre lider',
                key: 'pers_name'
            },
            {
                label: 'Puntaje equipo',
                key: 'team_effectiveness'
            },
            {
                label: 'Participacion',
                key: 'pers_score'
            },
        ],
        // Paginación Equipos
        paginationTeam: {
            currentPage: 1,
            perPage: 6
        },
        // Búsqueda Equipo
        filterTeam: '',
        // Campos proyectos
        projectFields: [
            {
                label: 'Nombre del proyecto',
                key: 'proj_name'
            },
            {
                label: 'Estado',
                key: 'isactive'
            },
            {
                label: 'Nombre de la tarea',
                key: 'task_name'
            },
            {
                label: 'Fecha de inicio',
                key: 'task_start_date'
            },
            {
                label: 'Fecha de fin',
                key: 'task_end_date'
            },
            {
                label: 'Participacion',
                key: 'participation'
            },
        ],
        paginationProject: {
            currentPage: 1,
            perPage: 6
        },
        // Busqueda proyoectos
        filterProject: ''
    },
    created(){
            if(window.location.pathname.substr(1, 25) == "reportes/equipos/miembro/"){
                this.personaId = window.location.pathname.substr(26, 36);
                this.listadoEquipos();
                this.listadoProyectos();
                this.detalleUsuario();
            }
    },
    methods: {
        listadoEquipos(){
            this.loader(true);
            axios({
                url: '/reportes/equipos/miembro/'+this.personaId+'/equipos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false);
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.equipos = response.data.data;
                    for(i=0; i < this.equipos.length; i++ ){
                        
                        if (this.equipos[i].pers_score > this.equipos[i].team_effectiveness){

                            this.equipos[i].pers_score = "Eficiente"

                        }else if (this.equipos[i].pers_score < this.equipos[i].team_effectiveness){
                            this.equipos[i].pers_score = "Poco eficiente"
                        }
                        this.equipos[i].pers_name += " " +this.equipos[i].pers_lastname
                    }
                }
            });
        },
        listadoProyectos(){
            this.loader(true);
            axios({
                url: '/reportes/equipos/miembro/'+this.personaId+'/proyectos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false);
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.proyectos = response.data.data;

                    for(i=0; i < this.proyectos.length; i++ ){
                        if (this.proyectos[i].isactive == 1){
                            this.proyectos[i].isactive = "Activo"
                        }else{
                            this.proyectos[i].isactive = "Inactivo"
                        }
                    }

                }
            });
        },
        detalleUsuario(){
            this.loader(true);
            axios({
                url: '/persona/detalle/'+this.personaId+'/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false);
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.persona = response.data.data;
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
            var equipos = this.equipos;
            if(filter){
                equipos = equipos.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return equipos;
        },
        filteredProject(){
            var filter = this.filterProject && this.filterProject.toLowerCase();
            var proyectos = this.proyectos;
            if(filter){
                proyectos = proyectos.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return proyectos;
        }

    }
})