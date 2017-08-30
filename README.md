# pixel_to_point
Este geoproceso ha sido desarrollado en el Servicio Nacional de Geología y Minería de Chile (http://http://www.sernageomin.cl/), específicamente en la Unidad de Sistemas de Información Geológico para la Unidad de Sensores Remotos. A petición de Paula Olea (paula.olea@sernageomin.cl) ha sido compartido a público.

El geoproceso responde a los siguientes requerimientos funcionales y no funcionales planteados:
* Despliegue de la geometría de puntos con nuevos campos que representan la fecha y hora de captura de cada imagen, llevada a horario local.
* El Geoproceso deberá asignar la referencia espacial si estas no tuviesen. Cabe destacar que el sistema de referencia asignado será WGS84 en coordenadas geográficas.
* La nueva capa solo debe llevar un campo de la capa original de puntos a elección del usuario.
* Se debe permitir escalar los resultados obtenidos ingresando como parámetro un valor de multiplicación.
* La fecha y hora de captura de las imágenes será obtenido del mismo nombre  de los archivos y llevado a horario local mediante un parámetro.
* Construcción modular y comentareada del código del geoproceso.
* Generación de archivo Log. Este archivo vuelca todas las operaciones del geoproceso, sean correctas o no. En otras palabras, la ejecución del geoproceso no se detendrá hasta que haya terminado de procesar todas las imágenes.


Básicamente esta herramienta fue desarrollada en ambiente ArcGIS Desktop 10.3.1 utilizando la extensión Spatial Analyst y la librería de arcpy; para ser instalada, se debe agregar la caja de herramienta (*.tbx) en arctoolbox o navegar hasta ella por arcCatalog y verificar los siguientes parámetros:
* En propiedades del script verificar la fuente del mismo, a pesar de que está configurado con rutas relativas.
* Verificar los parámetros de script, por ejemplo: formato de fecha, nombres y longitudes de campos de salida.

Parámetros de ejecución:
* “Ruta de rasters”: directorio donde se encuentran las imágenes, sean en su raíz o subdirectorios.
* “Puntos de muestra”: corresponde a la entidad geométrica que contiene los puntos de las imágenes.
* “Campo identificador”: campo de la entidad ingresada en el parámetro anterior que se mantendrá en la cobertura geográfica de salida.
* “Ruta de salida”: directorio donde se almacenarán los resultados.
* “Nombre carpeta de salida”: nombre del directorio de resultados.
* “Nombre entidad de salida”: nombre de la cobertura de salida.
* “Factor escala”: factor que escalará los valores encontrados en los píxeles identificados.
* “Ruta del log”: Directorio donde se almacenará el archivo Log.
* “Restar para Horario local (hrs.)”: Horas que se le restarán al horario UTC de captura de las imágenes con la finalidad de llevarlo a hora local.
* “Posición prefijo fecha-hora”: Posición contada desde 0 y desde el inicio del nombre del raster hasta la posición del primer caracter que define el string de fecha y hora del raster.
* “Posición sufijo fecha-hora”: Posición contada desde 0 y desde el inicio del nombre del raster hasta la posición del último caracter que define el string de fecha y hora del raster.

NOTA: es posible ejecuta la herramienta en cualqueir arcmap desde la versión 10.1; sin embargo, puede que haya que recrear la herramienta junto a sus parámetros y enrutar la script almacenada en la carpeta "SCRIPTS".
