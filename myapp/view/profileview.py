from django.shortcuts import render


# ==================== Perfil ================

##
# @brief Plantilla de Perfil de Usuario
# @param request instancia HttpRequest
# @return plantilla HTML
#
def perfilView(request):
    return render(request, "perfil/gestion.html")
