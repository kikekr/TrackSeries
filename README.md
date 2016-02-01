# TrackSeries
Aplicación de navegador desarrollada en Django. Gestiona una lista de series, y proporciona estadísticas de popularidad por países basadas en la compartición mediante torrent.
La dirección del recurso es /series/

## Fuentes de datos empleadas:
* https://thetvdb.com/
* https://freegeoip.net/
* https://kat.cr/

## Herramientas de administración
Además de la típica administración de base de datos proporcionada por Django (/admin/), los administradores también pueden forzar actualizaciones de todas las series así como forzar inicios de análisis.

## Ejecución de la aplicación
Se recomienda usar un usuario único donde ejecutar el servidor (pues emplea crontab y no respeta el contenido previo del mismo). Antes de iniciar el servidor, es ALTAMENTE recomendable actualizar todas las series mediante la orden "updateseries all" de manage.py para evitar incoherencias entre el API remoto y los datos locales.
