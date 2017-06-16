# Casos de prueba

## Previos
Aqui se especifican los casos de prueba hechos al recibir el código y antes de hacer algún cambio.

Los requisitos que se debiesen cumplir, y para los cuales se diseñaron los casos de prueba:

### Requisitos generales

#### R1. El sistema debe permitir la autentificación de usuarios.

Se supone que el usuario no está autentificado en el sistema.
Si el usuario no está registrado:
```
	1. Entrar a pagina web.
	2. Dirigir a 'Inciar Sesion'
	3. Dirigir a 'Registrate'
	4. Llenar la información de usuario.
	5. Enviar formulario (presionar 'registrarse)'
	6. Verificar que el usuario esté correctamente registrado y autentificado.
Pass!
```
Si el usuario está registrado como administrador, alumno, vendedor ambulante o fijo:
```
	1. Entrar a pagina web.
	2. Dirigir a 'Iniciar Sesión'.
	3. Ingresar información de autentificación.
	4. Enviar formulario (presionar 'iniciar sesión')
	5. Verificar que el usuario esté correctamente autentificado.

Pass, pero no hay sistema de persistir la sesión autentificada.
```
#### R2. El sistema debe considerar 4 tipos de usuarios: administrador, alumno, vendedor ambulante y vendedor fijo.
Si el usuario no está registrado, y se desea registrar como alumno, vendedor ambulate o fijo:
```
	1. Entrar a pagina web.
	2. Dirigir a 'Inciar Sesion'
	3. Dirigir a 'Registrate'
	4. Llenar la información de usuario. Al elegir tipo de usuario, seleccionar el elegido.
	5. Enviar formulario (presionar 'registrarse)'
Se espera que en este punto el usuario esté correctamente registrado y autentificado con la cuenta del tipo escojido.
Pass!
```
Si el usuario no está registrado, y se desea registrar como administrador:
```
	1. Entrar a pagina especial de registro de admins: signupAdmin/
	2. Llenar y enviar formulario.
Se espera que en este punto el usuario esté correctamente registrado y autentificado con la cuenta del tipo administrador.
Failed...
```
Si el usuario está registrado como algun tipo de cuenta:
```
	1. Entrar a pagina web.
	2. Dirigir a 'Iniciar Sesión'.
	3. Ingresar información de autentificación.
	4. Enviar formulario (presionar 'iniciar sesión')
Se espera que en este punto el usuario este correctamente  autentificado con la cuenta del tipo escojido.
Pass para todos excepto Administrador.
```
#### R3. El sistema debe permitir que vendedores ambulantes hagan check-in para aparecer como activos en el sistema.
Suponiendo que el usuario esta autentificado como vendedor ambulante.
```
	1. Mover switch en barra lateral hacia 'Si' para hacer Check-in.
	2. Mover switch en barra lateral hacia 'No' para hacer Check-out.
Al elegir cualquiera de las dos opciones, el estado debe reflejarse y persistir en la base de datos. Se visualiza en la vista de vendedor.
Pass!
```
#### R4. Los vendedores fijos estarán activos en el sistema durante el horario que declaren de atención en el sistema.
Suponiendo que el vendedor fijo existe, y por ello tiene un horario especificado.
```
	1. Durante las horas del día, entre la Hora de Incio y Hora de Término del vendedor, se debe mostrar su estado como activo en la vista de vededor.
	2. Durante las horas del día, no entre la Hora de Incio y Hora de Término del vendedor, se debe mostrar su estado como inactivo en la vista de vededor.
Pass!
```
### Ficha de vendedor (vista por alumno):
#### R11. El sistema debe mostrar el nombre y foto de perfil del vendedor.
Supone que el vededor existe, por lo tanto tiene foto de perfil y nombre.
```
	1. Ingresar a ficha del vendedor (presionando entrada en el mapa).
	2. Verificar que aparece la foto de perfil y nombre del vendedor.
Pass!
```
#### R12. El sistema debe mostrar un resumen del stock de producto que tiene disponible. Desde este resumen se puede navegar a las fichas de los productos individuales.	
Supone que el vendedor existe y posee al menos un producto.
```
	1. Ingresar a ficha de vendedor (presionando entrada en el mapa).
	2. Verificar que aparece stock de los productos.
	3. Verificar que se puede navegar a la fichas de productos individuales.
Pass!
```
#### R13. El sistema debe mostrar claramente si el vendedor esta activo o no.
Supone que el vendedor existe.
```
Vista desde ficha:
	1. Ingresar a ficha del vendedor (presionando entrada en el mapa).
	2. Verificar estado del vendedor en ficha.
Pass!
```
#### R14. El sistema debe mostrar las formas de pago aceptadas por el vendedor.
Supone que el vendedor existe.
```
Vista desde ficha:
	1. Ingresar a ficha del vendedor (presionando entrada en el mapa).
	2. Verificar estado las formas de pago en la ficha.
Pass!
```
#### R15. En el caso de los vendedores fijos, el sistema debe mostrar las horas de atención.
Supone que el vendedor fijo existe.
```
Vista desde ficha:
	1. Ingresar a ficha del vendedor (presionando entrada en el mapa).
	2. Verificar estado del vendedor en ficha.
Pass!
```
#### R16. El sistema debe permitir que los usuarios de tipo alumno registren a vendedores como “favorito”.
Supone que el vendedor fijo existe, y se esta autentificado como alumno.
```
	1. Ingresar a ficha del vendedor (presionando entrada en el mapa).
	2. Presionar deslizar switch bajo estrella de favorito a la derecha, para registrar favorito.
	3. Hacer log-out.
	4. Volver a auntentificar como el mísmo alumno.
	3. Verificar que favorito persiste
Pass!
```
### Ficha de vendedor (vista por un vendedor):
#### R17. El sistema debe permitir gestionar el nombre y foto de perfil del vendedor.
Supone que el vendedor esta registrado y autentificado.
```
	1. Presionar engranaje en barra lateral (izquierda).
	2. Cambiar nombre y/o foto de perfil.
	3. Verificar cambios en ficha de vendedor.
Pass!
```
#### R18. El sistema debe permitir gestionar el stock de producto que tiene disponible.
Supone que el vendedor esta registrado, autentificado y posee al menos 1 producto.
```
	1. Dirigir a ficha de vendedor (despues de hacer log-in/registrarse)
	2. Cambiar stock del producto desde edicion rapida, o desde engranaje (sobre el producto) para edicion completa.
	3. Verificar cambios en ficha de vendedor y producto.
Pass!
```
#### R19. En el caso de los vendedores ambulantes, el sistema debe permitir que el vendedor indique si esta activo o no.
Supone que el usuario esta autentificado como vendedor ambulante.
```
	1. Mover switch en barra lateral hacia 'Si' para hacer Check-in.
	2. Mover switch en barra lateral hacia 'No' para hacer Check-out.
	3. Verificar que, al elegir cualquiera de las dos opciones, el estado se refleja en el estado del vendedor.
	4. Verificar que persiste elección, luego de hacer log-out y volver a auntetificarse.
Pass!
```
#### R20. En el caso de los vendedores fijos, el sistema debe permitir gestionar las horas de atención.
Supone que el usuario esta autentificado como vendedor fijo.
```
	1. Presionar engranaje en barra lateral (izquierda).
	2. Cambiar horas de atención.
	3. Verificar cambios en ficha de vendedor.
Se debería reflejar el cambio en las visualizaciones de horarios y, dependiendo de las horas, en el estado del vendedor.
Pass!
```
#### R21. El sistema debe permitir gestionar las formas de pago aceptadas por el vendedor.
Supone que el vendedor esta registrado y autentificado.
```
	1. Presionar engranaje en barra lateral (izquierda).
	2. Cambiar las formas de pago.
	3. Verificar cambios en ficha de vendedor.
Pass!
```
#### R22. El sistema debe mostrar cuántos usuarios lo han seleccionado como “favorito”.
Supone la existencia de un vendedor (fijo o ambulante) y un alumno.
```
	1. Autentificarse como vendedor.
	2. Dirigir a ficha de vendedor y revisar cantidad de favoritos, al lado de la estrella.
	3. Cerrar sesión como vendedor y autentificarse como alumno.
	4. Dirigir a ficha del vendedor previo, y registrarlo como favorito.
	5. Cerrar sesion como alumno. Y autentificarse como vendedor.
	6.  Dirigir a ficha de vendedor, y volver a revisar cantidad de favoritos. 
	7. Verificar que la cantidad aumentó en 1.
	8. Cerrar sesión como vendedor y autentificarse como alumno.
	9. Quitar favorito.
	10. Cerrar sesion como alumno. Y autentificarse como vendedor.
	11.  Dirigir a ficha de vendedor, y volver a revisar cantidad de favoritos. 
	12. Verificar que la cantidad disminuyó en 1.
Pass!
```
### Ficha de producto:
#### R23. El sistema debe mostrar la siguiente información para un producto: nombre, foto,
categoría, descripción, stock, precio.
Supone que el vendedor existe y posee al menos un producto.
```
	1. Dirigir a vista de vendedor (presionando en mapa).
	2. Verificar al interactuar con producto que se muestra el nombre, foto, categoría, descripción, stock y precio.
Pass!
```
#### R24. En el caso de los vendedores, el sistema debe permitir gestionar la información de un
producto.
Supone que el vendedor existe, esta autentificado y posee al menos un producto.

```
	1. Dirigir a vista de vendedor (re-dirige despues de log-in).
	2. Acceder a edicion de producto precionando engranaje sobre alguno.
	3. Modificar algun sub-conjunto de los datos.
	4. Verificar cambios en ficha de vendedor.
Pass excepto categoría.
```

## Para esta iteración:

###Interfaz de búsqueda de vendedores:
#### R5. El sistema debe mostrar un mapa centrado en la posición actual del usuario, sin importar si hay un usuario autentificado.
```
    1. Ingresar a la pagina web.
    2. Verificar que se visualiza mapa centrado en la posicion actual.
```

#### R6. El sistema debe mostrar las posiciones de los vendedores activos con stock disponible en este mapa, sin importar si hay un usuario autentificado.
Supone que hay al menos un vendedor activos con stock disponible en el área cercana.
```
    1. Ingresar a la pagina web.
    2. Verificar que se visualiza mapa mostrándose el vendedor activo con stock dispoible.
```

#### R7. Si el usuario se ha autentificado como alumno, el sistema también debe mostrar las posiciones de los vendedores favoritos activos del usuario.
Supone que el alumno está autentificado y posee al menos un vendedor favorito que esta activo en el área cercana.
```
    1. Ir al Home.
    2. Verificar que vendedor favorito se muestra en pantalla.
```

#### R8. Se debe usar iconos distintos para los vendedores favoritos/no favoritos.
Supone que el alumno está autentificado y posee al menos un vendedor favorito activo en el área cercana.
Además, que que existe al menos un vendedor no-favorito activo en el área cercana.
```
    1. Ir al Home.
    2. Verificar que los vendedoros favoritos y no-favoritos se muestran en pantalla con íconos distintos.
```
#### R9. Cuando un usuario presiona el icono de un vendedor en el mapa, el sistema debe mostrar la ficha de este vendedor.
Supone que hay iconos de vendedores en el mapa.
```
    1. Ir al Home.
    2. Verificar que al presionar sobre un icono de vendedor, el sistema muestra la ficha de este vendedor.
```
#### R10. El sistema debe permitir filtrar los vendedores en el mapa, mostrando solo los vendedores que tienen stock disponible de productos que pertenecen a las categorías especificadas por el usuario (sin importar si hay un usuario autentificado).
Supone al menos un vendedor activo en el área cercana con al menos un producto con stock > 1.

```
    1. Ir al Home.
    2. Abrir modal de filtros (TODO)
    3. Elegir al menos una categoría.
    4. Verificar que todos los vendedores en el mapa poseen stock de productos de las categorías seleccionadas.
```
#### R25: Los usuarios de tipo alumno y vendedor ambulante deben poder lanzar una alerta cuando vean a los carabineros. El sistema debe lanzar una advertencia a los vendedores ambulantes que estén en un radio de 15 metros del usuario que lanzo la alerta.
Supone un usuario autentificado tipo alumno o vendedor ambulante. Además, supone al menos un vendedor ambulante en un radio de 15 metros del usuario.
```
    1. Ir a alerta. (TODO)
    2. Presionar alerta de carabineros.
    3. Confirmar.
    4. Verificar que a los vendedores ambulantes en un radio de 15 metros les aparece la advertencia.
    
```