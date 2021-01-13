let gestionPlantilla = new Vue({
    el: '#gestion-plantillas',
    delimiters: ['[[', ']]'],
    data: {
        almacenamientoPlantilla: {},
        plantillas: [],
        plantillaEdicion: {},
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        // Búsqueda
        filter: '',
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'team_name'
            },
            {
                label: 'Descripcion',
                key: 'team_description'
            },
            {
                label: 'Efectividad',
                key: 'team_effectiveness'
            },
            {
                label: 'Nombre lider',
                key: 'pers_name'
            },
            {
                label: 'Miembros',
                key: 'team_miembros'
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    created(){

        if(window.location.pathname == '/equipos/'){
            this.listadoPlantillas();
        }
    },
    methods: {
        listadoPlantillas(){

            axios({
                url: '/plantillas-equipo/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){
                    this.plantillas = response.data.data;
                    for(i=0; i < this.plantillas.length; i++ ){
                        this.plantillas[i].pers_name += " " +this.plantillas[i].pers_lastname
                    }
                }

            })
        },
        eliminarPlantilla(planid){

            Swal.fire({
                text: 'Estas seguro?. Es irreversible',
                type: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Si',
                cancelButtonText: 'No',
            })
            .then(result => {

                if(result.value){

                    axios({
                        url: '/plantillas-equipo/' + planid + '/delete/',
                        method: 'DELETE',
                        headers: {
                            Authorization: getToken(),
                        }
                    })
                    .then(response => {

                        if(response.data.code == 200 && response.data.status == 'success'){

                            this.listadoPlantillas();

                            Swal.fire({
                                title: 'Exito',
                                text: 'Equipo Eliminado',
                                type: 'success'
                            })
                        }
                    })
                    .catch(response => {

                        this.listadoPlantillas();
   
                        Swal.fire(
                         'Error!',
                         'No es posible eliminar el equipo debido a que está vinculado a un proyecto',
                         'error'
                       );
                   });
                }
            });
        },
        guardarPlantilla(){
            queryString = Object.keys(this.almacenamientoPlantilla).map(key => {

                return key + "=" + this.almacenamientoPlantilla[key];
            })
            .join('&');

            axios({
                url: '/plantillas-equipo/store/',
                data: queryString,
                method: 'POST',
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {

                if(response.data.code == 201 && response.data.status == 'success'){

                    $("#agregar-plantilla").modal('hide');
                    this.almacenamientoPlantilla = {}
                    this.listadoPlantillas();

                    Swal.fire({
                    title: 'Exito!',
                    text: 'Equipo creado satisfactoriamente',
                    type: 'success',
                    confirmButtonText: 'Acepto'
                    });
                }
            })
            .catch(response => {

                $("#agregar-plantilla").modal('hide')
                this.almacenamientoPlantilla = {};

                Swal.fire({
                  title: 'Error!',
                  text: 'Ya existe un equipo con el nombre digitado, verifica la información',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        editarPlantilla(){

            queryString =  Object.keys(this.plantillaEdicion).map(key => {
                return key + "=" + this.plantillaEdicion[key];
            }).join('&');

            axios({
                url: '/plantillas-equipo/' + this.plantillaEdicion.team_id+'/',
                method: 'PUT',
                data: queryString,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.listadoPlantillas();
                    $("#editar-plantilla").modal('hide');

                    Swal.fire({
                        title: 'Exito',
                        text: 'Equipo modificado',
                        type: 'success',
                    });
                }
            })
            .catch(() => {

                $("#editar-plantilla").modal('hide');

                Swal.fire(
                    'Error!',
                    'Ya existe un equipo con el nombre digitado, verifica la información',
                    'error'
                );
            });
        }
    },
    computed: {
        filteredTeams(){

            var filter = this.filter && this.filter.toLowerCase();
            var plantillas = this.plantillas;

            if(filter){

                var plantillas = plantillas.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return plantillas;
        }
    }
})