from django.conf.urls import url
from main import views
urlpatterns = [
    url(r'^$', views.index, name='index'),

    # public
    url(r'^vistaVendedorPorAlumnoSinLogin/', views.vistaVendedorPorAlumnoSinLogin,
        name='vistaVendedorPorAlumnoSinLogin'), # vista de mapa publico para usuario no autentificado

    # auth
    url(r'^login/$', views.login,name='login'), # log-in view
    url(r'^loginReq/', views.loginReq, name='loginReq'), # al apretar boton login, metodo POST lleva aqui
    url(r'^signup/$', views.signup,name='signup'), # sign-up view
    url(r'^verificarEmail/$', views.verificarEmail, name='verificarEmail'), # url submit POST para verificar el email ingresado en sign-ip.
    url(r'^register/', views.register, name='register'),  # al apretar registrar, metodo POST lleva aqui
    url(r'^logout/', views.logout, name='logout'), # al apretar log-out
    url(r'^signupAdmin/$', views.signupAdmin, name='signupAdmin'), # vista de sign-up de admin
    url(r'^registerAdmin/$', views.registerAdmin, name='registerAdmin'), # al apretar registrar admin (bug)
    url(r'^loginAdmin/$', views.loginAdmin, name='loginAdmin'), # vista de log-in de admin (bug)

    # edicion
    url(r'^editarVendedor/$', views.editarVendedor, name='editarVendedor'), # vista de pagina de edicion
    url(r'^editarDatos/$', views.editarDatos, name='editarDatos'), # al apretar editar lleva aqui

    # alumno
    url(r'^inicioAlumno/', views.inicioAlumno, name='inicioAlumno'), # home al logearse como alumno
    url(r'^vistaVendedorPorAlumno/', views.vistaVendedorPorAlumno, name='vistaVendedorPorAlumno'), # ficha de vendedor vista por alumo
    url(r'^editarPerfilAlumno/', views.editarPerfilAlumno, name='editarPerfilAlumno'), # vista de edicion alumno
    url(r'^procesarPerfilAlumno/', views.procesarPerfilAlumno, name='procesarPerfilAlumno'), # al apretar editar, POST
    url(r'^cambiarFavorito/', views.cambiarFavorito, name='cambiarFavorito'), # url para hacer submit de una forma para cambiar favorito.

    # vendedor ambulante
    url(r'^cambiarEstado/$', views.cambiarEstado, name='cambiarEstado'), # url submit GET ara cambiar estado.

    # admin (no se ha testeado nada de aqui)
    url(r'^borrarUsuario/', views.borrarUsuario, name='borrarUsuario'),
    url(r'^agregarAvatar/', views.agregarAvatar, name='agregarAvatar'),
    url(r'^adminEdit/$', views.adminEdit, name='adminEdit'),
    url(r'^editarUsuarioAdmin/$', views.editarUsuarioAdmin, name='editarUsuarioAdmin'),
    url(r'^editarUsuario/', views.editarUsuario, name='editarUsuario'),

    # vendedores (productos)
    url(r'^gestionproductos/$', views.gestionproductos, name='gestionproductos'), # vista para agregar producto
    url(r'^productoReq/', views.productoReq, name='productoReq'), # al apretar agregar o editar
    url(r'^borrarProducto/', views.borrarProducto, name='borrarProducto'), # url submit GET al apretar eliminar producto
    url(r'^editarProducto/', views.editarProducto, name='editarProducto'), # url submit GET al apretar editar
    url(r'^getStock/$', views.getStock, name='getStock'), # url submit GET para obtener stock
    url(r'^createTransaction/$', views.createTransaction, name='createTransaction'), # al modificar stock en ficha de vendedor

    # estadisticas
    url(r'^fijoDashboard/$', views.fijoDashboard, name='fijoDashboard'), # vista ficha con graficos para fijo
    url(r'^ambulanteDashboard/$', views.ambulanteDashboard, name='ambulanteDashboard'), # vista ficha con graficos para ambulante

    # un-used
    url(r'^formView/', views.formView, name='formView'), # vista bugeada, no se sabe para que sirve
    url(r'^vendedorprofilepage/$', views.vendedorprofilepage, name='vendedorprofilepage'), # lleva a una ficha de vendedor estatica
    url(r'^loggedin/', views.loggedin, name='loggedin'), # muestra una pagina en blanco con un texto que parece de debugeo

]
