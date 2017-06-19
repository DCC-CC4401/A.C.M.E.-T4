from main.models import Usuario
from django.core.exceptions import ObjectDoesNotExist

def user_processor(request):
    dict = {}
    dict['logged_auth'] = False
    dict['logged_seller_isActive'] = False
    if request.user.is_authenticated():
        duser = request.user
        dict['logged_django_user'] = duser
        try:
            usuario = Usuario.objects.get(django_user=duser)
            dict['logged_user'] = usuario
            dict['logged_auth'] = True
            dict['logged_name'] = usuario.nombre
            dict['logged_avatar'] = str(usuario.avatar)
            dict['logged_seller_isActive'] = usuario.activo
        except ObjectDoesNotExist:
            pass
    return dict