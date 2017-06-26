from django.conf.urls import url
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, {'template_name': 'main/login.html'}, name='login'),
    url(r'^signup/$', views.signup,name='signup'),
    url(r'^loginReq/',views.loginReq, name = 'loginReq'),
    url(r'^gestionproductos/$', views.gestionproductos,name='gestionproductos'),
    url(r'^formView/', views.formView, name='formView'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/', views.register, name='register'),
    url(r'^loggedin/', views.loggedin, name='loggedin'),
    url(r'^productoReq/', views.productoReq, name='productoReq'),
    url(r'^cambiarEstado/$', views.cambiarEstado,name='cambiarEstado'),
    url(r'^editarVendedor/$', views.editarVendedor,name='editarVendedor'),
    url(r'^editarDatos/$', views.editarDatos,name='editarDatos'),
    url(r'^inicioAlumno/', views.inicioAlumno, name='inicioAlumno'),
    url(r'^borrarUsuario/', views.borrarUsuario, name='borrarUsuario'),
    url(r'^borrarProducto/', views.borrarProducto, name='borrarProducto'),
    url(r'^editarProducto/', views.editarProducto, name='editarProducto'),
    url(r'^cambiarFavorito/', views.cambiarFavorito, name='cambiarFavorito'),
    url(r'^editarPerfilAlumno/', views.editarPerfilAlumno,name='editarPerfilAlumno'),
    url(r'^procesarPerfilAlumno/', views.procesarPerfilAlumno,name='procesarPerfilAlumno'),
    url(r'^editarUsuario/', views.editarUsuario, name='editarUsuario'),
    url(r'^agregarAvatar/', views.agregarAvatar, name='agregarAvatar'),
    url(r'^signupAdmin/$', views.signupAdmin,name='signupAdmin'),
    url(r'^registerAdmin/$', views.registerAdmin,name='registerAdmin'),
    url(r'^EstadisticasRango/$', views.estadisticasRango, name='porHorario'),
    url(r'^getStock/$', views.getStock,name='getStock'),
    url(r'^verificarEmail/$', views.verificarEmail,name='verificarEmail'),
    url(r'^adminEdit/$', views.adminEdit,name='adminEdit'),
    url(r'^editarUsuarioAdmin/$', views.editarUsuarioAdmin,name='editarUsuarioAdmin'),
    url(r'^loginAdmin/$', views.loginAdmin, name='loginAdmin'),
    url(r'^createTransaction/$', views.createTransaction, name='createTransaction'),
    url(r'^estadisticasVendedor/$', views.estadisticasVendedor, name='estadisticasVendedor'),
    url(r'^fichaVendedor/(\d*)$', views.fichaVendedor, name='fichaVendedor'),


]
