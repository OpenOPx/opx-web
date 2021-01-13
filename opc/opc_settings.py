from myapp.models import Params

def getDBSettings():

    parametros = Params.objects.all()
    settings = {}

    for p in parametros:
        settings[p.params_id] = p.params_value

    return settings

settings = getDBSettings()
