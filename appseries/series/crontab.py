# -*- coding: utf-8 -*-
import os, errno
from datetime import datetime

path = "/tmp/.appseries/test"
programPath = "/home/christian/Git/proint/"

def readFileContent(file_path):
    # Comprobar si el fichero existe
    if os.path.exists(file_path):
        # Leer el fichero y devolverlo
        return [line.strip() for line in open(file_path, "r")]
    else:
        return []


def writeFileContent(file_path, content):
    # Comprobar si existe el directorio
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Escribir el contenido del fichero
    f = open(file_path, 'w')
    for line in content:
        f.write("%s\n" % line)

def saveTempChanges(file_path):
    # Clear previous crontab
    os.system("crontab -r")

    # Load new crontab file onto the system
    os.system("crontab " + file_path)

def setDailyUpdate():
    content = readFileContent(path)
    header = "# Daily data update"
    crontabLine = "0 0 * * * ./manage.py updateEverything >/dev/null 2>&1"

    # Busca la cabecera y actualiza la línea
    for lineNumber in xrange(0, len(content)):
        if (content[lineNumber] == header):
            content[lineNumber+1] = crontabLine
            writeFileContent(path, content)
            return

    # De no encontrarla, se escribe al final del fichero cabecera y linea de crontab
    content.append(header)
    content.append(crontabLine)
    writeFileContent(path, content)

def setAnalysisSchedule(episode):
    content = readFileContent(path)
    airDate = datetime.fromtimestamp(episode.airDate)

    # Si la fecha de emisión es futura, establecer un análisis
    if (airDate - datetime.utcnow()).total_seconds()>0:
        header = "# %i %i" % (episode.serie.id, episode.id)
        crontabLine = "0 0 %i %i * " % (airDate.day, airDate.month) + programPath + "appseries/manage.py " + \
            "startanalysis %i %i %i >/dev/null 2>&1" % (episode.serie.id, episode.temporada, episode.numero)

        content = readFileContent(path)
        # Buscar cabecera del capitulo
        for lineNumber in xrange(0, len(content)):
            if content[lineNumber] == header:
                content[lineNumber+1] = crontabLine
                writeFileContent(path, content)
                return

        # Si no se encuentra la cabecera -> se añade al final
        content.append(header)
        content.append(crontabLine)
        writeFileContent(path, content)
