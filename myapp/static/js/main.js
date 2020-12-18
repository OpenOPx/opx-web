window.kpiUrl = "http://kf.variamos.com/#/forms";
// window.kpiUrl = "https://kobo.humanitarianresponse.info/#/forms/";

window.getToken = function(){

    let userInfo = JSON.parse(sessionStorage.getItem('userinfo'));

    if(userInfo != null && typeof userInfo == 'object' && userInfo.hasOwnProperty('token')){


        return 'Bearer ' + userInfo.token;

    } else if(window.location.pathname != '/'){

        return location.href = '/';
    }

}

window.getUser = function(){

    let userInfo = JSON.parse(sessionStorage.getItem('userinfo'));

    if(userInfo != null && typeof userInfo == 'object' && userInfo.hasOwnProperty('user')){

        return userInfo.user;

    } else{

        return location.href = '/';
    }
}

window.logout = function(){


    sessionStorage.removeItem('userinfo');
    location.href = "/";
}

window.getInfoChart = function(diagram, evt){

  var activePoints = diagram.getElementsAtEvent(evt);
  var response = "";

  if (activePoints[0]) {
    var chartData = activePoints[0]['_chart'].config.data;
    var idx = activePoints[0]['_index'];

    var label = chartData.labels[idx];
    var value = chartData.datasets[0].data[idx];

    response = label;

  } else{

    response = false;
  }

  return response;
}

// Vue.js
window.Vue = require('vue');

// Axios
window.axios = require('axios');

// Moment.js
window.moment = require('moment');

// Sweet Alert 2
import Swal from 'sweetalert2';

// Vue Multiselect
import Multiselect from 'vue-multiselect';

// Bootstrap Vue
import BootstrapVue from 'bootstrap-vue';

// Vue DatePicker
import Datepicker from 'vuejs-datepicker';

// Leaflet
require('./plugins/leaflet/leaflet.js');

// Leaflet Draw
require('leaflet-draw/dist/leaflet.draw.js');

//TinyMCE
import Editor from '@tinymce/tinymce-vue';

// Agregando el componente Multiselect
Vue.component('multiselect', Multiselect);

// Agregando Bootstrap Vue
Vue.use(BootstrapVue);

// Agregando Componente Datepicker
Vue.component('datepicker', Datepicker);

// Agregando componente TinyMCE
Vue.component('editor', Editor);

// Filtro de estado de las entidades
Vue.filter('estado-entidad', function(value){

    if(value == 1){

        return "Activo";

    } else if(value == 0){

        return "Inactivo";
    }

});

Vue.filter('iniciales-usuario', function(value){

    let nombreSeparado = value.split(' ');
    let iniciales = "";

    for(let i=0; i<nombreSeparado.length; i++){

        iniciales += nombreSeparado[i].charAt(0);
    }

    return iniciales;
});

Vue.filter('fechas', function(value){

    return value.substr(0, 10);
});

Vue.filter('estadoTareasRedimension', function(value){

    let response = "";

    if(value){

        response = "<i class='material-icons'> check_circle_outline </span>"

    } else{

        response = "<i class='material-icons'> cancel </span>";
    }

    return response;
});

// const webdriver = require('selenium-webdriver');
// const chrome = require('selenium-webdriver/chrome');

// Instancia Vue para Gestión de Tipos de Proyecto
require('./components/proyectos/tiposProyecto').tiposProyecto;

// Instancia Vue para Gestión de proyectos
require('./components/proyectos/proyectos').proyecto;

// Instancia Vue para Gestión de Tareas
require('./components/tareas').tarea;

// Instancia Vue para Gestión de Instrumentos
require('./components/instrumentos').instrumento;

// Instancia Vue para Gestión de Decisiones
require('./components/decisiones').decision;

// Instancia Vue para Gestión de Usuarios
require('./components/usuarios').usuario;

// Instancia Vue para gestión de Roles
require('./components/roles').rol;

// Gestión de Permisos
require('./components/permisosRol.js');

// Gestión de Autenticación
require('./components/login').login;

// Gestión de Contextos
require('./components/contextos').contexto;

// Gestión de Datos de Contexto
require('./components/datosContexto').datoContexto;

// Información de Encuestas
require('./components/informacion-encuesta').informacionEncuesta;

// Recuperación de contraseña
require('./components/passwordReset').passwordReset;

// Equipos de Proyectos
require('./components/equipos').equipo;

// Gestión de proyectos - Proyectista
require('./components/proyectos/gestion-proyectos-mapa').gestionProyecto;

// Estadisticas
require('./components/reportes/antes').estadisticas;
require('./components/reportes/durante').estadisticas;
require('./components/reportes/despues').estadisticas;
require('./components/reportes/detalle').estadisticas;

// Gestión de Plantillas de Equipo
require('./components/plantillas/plantillasEquipo').gestionPlantilla;

// Gestión de Miembros de plantillas de equipo
require('./components/plantillas/miembrosPlantilla').miembrosPlantilla;

// Perfil
require('./components/perfil/informacion').informacionPerfil;
require('./components/perfil/gestion').gestionPerfil;

// Estilos
import './../scss/app/app.scss';
