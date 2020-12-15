Manual de despliegue
====================

Aplicación OPC/SPCC
===================

Contenido
---------

1. Objetivo

2. Prerrequisitos

3. Estructura de Archivos

4. Tabla de Componentes a Instalar

5. Descripción de instalación

6. Plan de retorno

7. Anexos

8. Información del manual y control de cambios

1.  **Objetivo**

>   El presente manual busca de forma sistemática orientar a DATIC en el proceso
>   de despliegue de la aplicación web y API REST desarrollados por Neuromedia;
>   Buscando así una normalización de cada uno de los procedimientos que hacen
>   parte del mismo.

>   A lo largo del presente se evidenciarán los pasos necesarios para poder
>   obtener como resultado final un producto de calidad implantado en la
>   infraestructura tecnológica de DATIC.

1.  **Prerrequisitos**

El encargado del despliegue de la aplicación deberá tener lo siguiente:

-   Usuario con rol de administrador en el sistema operativo de su preferencia.

-   Usuario Github con permisos sobre el repositorio de la aplicación

1.  **Estructura de Archivos**

>   A continuación, se expondrá la estructura de directorios que hacen parte de
>   la base del código:

>   **/opc/:**

>   En este directorio residen los archivos de configuración que permiten la
>   ejecución adecuada del sistema.

>   **/myapp/:**

>   En este directorio se encuentran el código principal del sistema. De aquí se
>   desprenden varios subdirectorios de gran importancia.

>   **/myapp/middleware/:**

>   En este directorio se encuentra el middleware que adiciona cabeceras CORS
>   con el fin de que el API REST sea consumida desde cualquier dispositivo.

>   **/myapp/static/:**

>   En este directorio residen los archivos estáticos del sistema. Tales como
>   css, js.

>   **/myapp/view /:**

>   En este directorio se encuentran las vistas(lógica de negocio) del sistema.
>   Alli se controlan los siguientes aspectos:

-   Autenticación

-   Gestión de Equipos

-   Estadísticas

-   Notificaciones

-   Comunicación Open Street Maps

-   Gestión de proyectos

-   Gestión de Tipos de Proyecto

-   Gestión de Tareas

**/myapp/view/views.py**

>   En este archivos residen las vistas(lógica de negocio) que controlan los
>   siguientes aspectos del sistema:

-   Gestión de usuarios

-   Gestión de Contextos

-   Gestión de Decisiones

-   Gestión de Roles y Permisos

-   Gestión de instrumentos

-   Comunicación KoboToolbox

-   Comunicación Tasking Manager

1.  **Tabla de componentes a instalar**

A continuación, se ponen de manifiesto cada una de los componentes necesarios
para el correcto funcionamiento de la aplicación. Cabe recalcar que el proceso
de instalación depende del sistema operativo seleccionado, por ello se provee la
documentación en la que se detalla la instalación de cada uno de ellos.

| Nombre        | Descripción                      | Documentación          |
|---------------|----------------------------------|------------------------|
| GIT           | Sistema de Control de Versiones  | [Ver Anexo a](#Anexos) |
| Python        | Lenguaje de Programación         | [Ver Anexo b](#Anexos) |
| Pip           | Gestor de paquetes para Python   | [Ver Anexo c](#Anexos) |
| Nginx         | Servidor web                     | [Ver anexo d](#Anexos) |
| PostgreSQL 10 | Sistema Gestor de Bases de Datos | [Ver Anexo e](#Anexos) |

1.  **Descripción de Instalación**

Habiendo instalado las herramientas mencionadas con anterioridad procedemos con
el proceso de instalación de la aplicación. A continuación, se describen los
pasos necesarios para lograr este objetivo:

1.  **Clonar el repositorio de Github**

>   Para hacer esto el usuario de github que se utilice debe tener los permisos
>   necesarios; ahora ejecutamos el siguiente comando en la máquina destino, el
>   cual nos permite obtener el código base de la aplicación desde un
>   repositorio de GIT alojado en un servidor remoto:

>   git clone https://github.com/mauriciosedano/opx-opensource-web.git

1.  **Crear entorno virtual para el Proyecto**

Este entorno nos permite aislar las librerías y ejecutables del proyecto con el
fin de evitar conflictos con otros recursos presentes en la máquina. [(Ver anexo
f)](#Anexos)

1.  **Instalar dependencias de python de la aplicación:**

Ahora necesitamos instalar las librerías y ejectuables requeridas por la
aplicación con el fin de obtener un funcionamiento adecuado de la misma.
Ejecutamos el siguiente comando dentro del directorio raíz de la aplicación:

pip install –r requirements.txt

1.  **Creación de base de datos**

Ahora procedemos a crear la base de datos de la aplicación. Habiendo hecho esto
en el motor de base de datos postgreSQL ejecutamos el siguiente comando en el
directorio raíz de la aplicación con el fin de importar la estructura y
contenido.

\\c db.sql

1.  **Configuración de la aplicación**

En esta sección debemos modificar el archivo de configuración
**opc/settings.py** en el cual especificaremos los datos de conexión a la base
de datos[(ver anexo g)](#Anexos); en el archivo debemos diligenciar los
siguientes campos:

>   **HOST:** Dirección ip del servidor de base de datos; en tal caso se
>   encuentre en la misma maquina especificar **localhost**.

>   **PORT:** El puerto de conexión al servidor de base de datos.

>   **NAME:** Nombre de la base de datos;

>   **USER:** Usuario con privilegios sobre la base de datos.

>   **PASSWORD:** Contraseña del usuario.

1.  **Despliegue de servidor web WSGI**

En este paso utilizaremos Gunicorn el cual es un servidor HTTP de interfaz de
puerta de enlace de servidor web Python el cual nos permite servir los recursos
del lado del servidor. Para esto ejecutamos el siguiente comando en el
directorio raíz:

gunicorn –bind 0:55555 opc.wsgi:application --daemon

1.  **Configuración del servidor web**

Para este paso debemos configurar NGINX con un proxy inverso, el cual nos
permite redirigir el tráfico a gunicorn y a su vez nos permite servir los
archivos estáticos de la aplicación tales como HTML, JS, CSS, PNG, JPG, etc.
Para ello debemos acceder al archivo de configuración e introducir un bloque de
servidor que permita este ajuste [(ver anexo h)](#Anexos); aquí debemos
configurar la ruta **static** con respecto al directorio static del directorio
base ubicando en **/myapp/static/**.

1.  **Plan de retorno**

En tal caso el proceso de instalación presente incovenientes se debe verificar
principalmente la existencia en el servidor de todas las herramientas
mencionadas con anterioridad.

Cabe recalcar que Neuromedia estará atento al proceso, con el fin de resolver
las dudas que sean necesarias aclarar dado que no es un proceso sencillo.

1.  **Anexos**

2.  https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

3.  https://tutorial.djangogirls.org/es/python_installation/

4.  https://www.makeuseof.com/tag/install-pip-for-python/

5.  http://nginx.org/en/docs/install.html

6.  https://tutorial-extensions.djangogirls.org/es/optional_postgresql_installation/

7.  http://docs.python.org.ar/tutorial/3/venv.html

![](media/6ffbdd3c2f02f2fc7a370fd9a61cf937.png)

![](media/5dc52860efcdd1f841854e4acae201d9.png)

1.  **Información del Manual y control de cambios**

| Título       | Manual de despliegue OPC/SPCC |
|--------------|-------------------------------|
| Versión      | 0.0.1                         |
| Autor        | Neuromedia                    |
| Revisado por | Juan Camilo Salazar           |
| Aprobado por | Carlos Duque                  |

**Registro de Cambios**

| Versión | Causa del Cambio | Responsable del Cambio | Área | Fecha del Cambio |
|---------|------------------|------------------------|------|------------------|
|         |                  |                        |      |                  |
|         |                  |                        |      |                  |
|         |                  |                        |      |                  |
|         |                  |                        |      |                  |

