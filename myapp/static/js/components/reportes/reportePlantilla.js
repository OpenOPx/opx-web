reportePlantilla = new Vue({
    el: '#reportes-miembros',
    delimiters: ['[[', ']]'],
    data: {
        plantillaID: '',
        loading: false,
        miembrosPlantilla: [],
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'pers_name'
            },
            {
                label: 'Fecha de nacimiento',
                key: 'pers_birthdate'
            },
            {
                label: 'Puntaje promedio',
                key: 'pers_score'
            },
            {
                label: 'Teléfono',
                key: 'pers_telephone'
            },
            {
                label: 'Estado',
                key: 'isactive'
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
    },
    created(){
        window.setTimeout(() => {
            if(window.location.pathname.substr(1, 17) == "reportes/equipos/" && window.location.pathname.substr(54, 64) == "/miembros/"){
                this.plantillaID = window.location.pathname.substr(18, 36);
                this.listadoMiembros();
            }

        }, 1000);
    },
    methods: {
        listadoMiembros(){
            this.loader(true);
            axios({
                url: '/miembros-plantilla/' + window.location.pathname.substr(18, 36) + '/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false);
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.miembrosPlantilla = response.data.data;
                    for(i=0; i < this.miembrosPlantilla.length; i++ ){
                        
                        this.miembrosPlantilla[i].pers_name += " " +this.miembrosPlantilla[i].pers_lastname
                    }
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

    }
})