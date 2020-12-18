from myapp.models import Parametro

def getDBSettings():

    parametros = Parametro.objects.all()
    settings = {}

    for p in parametros:
        settings[p.paramid] = p.paramvalor

    return settings

settings = getDBSettings()
