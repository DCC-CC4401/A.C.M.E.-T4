import datetime

import math

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import json
import requests
from django.utils import timezone
from .forms import LoginForm
from .forms import GestionProductosForm
from .forms import editarProductosForm
from .models import Usuario
from .models import Lugar
from .models import Comida
from .models import Favoritos
from .models import Imagen
from .models import Transacciones
from django.db.models import Count
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.http import HttpResponse
import simplejson
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from multiselectfield import MultiSelectField
from django.core.files.storage import default_storage
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.
def index(request):
    vendedoresJson = sellerList(request, 0)

    if request.user.is_authenticated():
        users = Usuario.objects.filter(django_user=request.user)

        f = Favoritos.objects.filter(idAlumno=users[0].id).values_list('idVendedor')
        f_json = json.dumps(list(f), cls=DjangoJSONEncoder)

        if len(users) > 0:
            if users[0].tipo == 2 or users[0].tipo == 3:
                return fichaVendedor(request, users[0].id)
            else:
                send_url = 'http://freegeoip.net/json'
                r = requests.get(send_url)
                j = json.loads(r.text)
                lat = j['latitude']
                lon = j['longitude']
                l = Lugar(lat=lat, lng=lon, acurracy=0, usuario=users[0])
                l.save()
    else:
        f_json = []

    lugares = Lugar.objects.filter().values_list('lat', 'lng', 'acurracy', 'usuario')
    lugares_json = json.dumps(list(lugares), cls=DjangoJSONEncoder)

    v = Usuario.objects.filter(Q(tipo=2) | Q(tipo=3)).values_list('nombre')
    v_json = json.dumps(list(v), cls=DjangoJSONEncoder)

    return render(request, 'main/index.html',
                  {"vendedores": vendedoresJson, "lugares": lugares_json,
                   "vendedoresNombres": v_json, "favoritos": f_json})

def tiempo(p):
    hi = p.horarioIni
    hf = p.horarioFin
    horai = hi[:2]
    horaf = hf[:2]
    mini = hi[3:5]
    minf = hf[3:5]
    tiempo = str(datetime.datetime.now().time())
    hora = tiempo[:2]
    minutos = tiempo[3:5]
    estado = ""
    if horaf >= horai: # caso 12 - 16
        if horaf >= hora and hora >= horai:
            if horai == hora:
                if minf >= minutos and minutos >= mini:
                    estado = "activo"
                else:
                    estado = "inactivo"
            elif horaf == hora:
                if minf >= minutos and minutos >= mini:
                    estado = "activo"
                else:
                    estado = "inactivo"
            else:
                 estado = "activo"
        else:
            estado = "inactivo"
    else: # caso 23:00 - 5:00
        if horaf <= hora and horai <= hora:
            if horai == hora:
                if minf >= minutos and minutos >= mini:
                    estado = "activo"
                else:
                    estado = "inactivo"
            elif horaf == hora:
                if minf >= minutos and minutos >= mini:
                    estado = "activo"
                else:
                    estado = "inactivo"
            else:
                estado = "activo"
        else:
            if '00' <= hora and hora <= horaf:
                if horai == hora:
                    if minutos >= mini:
                        estado = "activo"
                    else:
                        estado = "inactivo"
                else:
                    estado = "activo"
            else:
                estado = "inactivo"


    return estado

def sellerList(request,int):
    vendedores = []
    vendAmb = []
    if request.user.is_authenticated():
        users = Usuario.objects.filter(django_user=request.user)
    # lista de vendedores
    for p in Usuario.objects.raw('SELECT * FROM usuario'):
        if p.tipo == 2 or p.tipo == 3:
            if int == 1:
                if request.user.is_authenticated() and p.tipo == 3 and p != users[0]:
                    vendAmb.append(p.id)
            vendedores.append(p.id)
    vendedoresJson = simplejson.dumps(vendedores)
    vendedoresAmb = simplejson.dumps(vendAmb)
    # actualizar vendedores fijos
    for p in Usuario.objects.raw('SELECT * FROM usuario'):
        if p.tipo == 2:
            estado = tiempo(p)
            if estado == "activo":
                Usuario.objects.filter(nombre=p.nombre).update(activo=1)
            else:
                Usuario.objects.filter(nombre=p.nombre).update(activo=0)
    vendedoresJson = simplejson.dumps(vendedores)
    if int == 0:
        return vendedoresJson
    else:
        return vendAmb

def estadisticasRango(request):
    if request.user.is_authenticated():
        fini= request.POST.get("fechaIni");
        ffin = request.POST.get("fechaFin");
        usuario = Usuario.objects.get(django_user=request.user)
        id = usuario.id
        if usuario.tipo is 2:  ## Vendedor fijo
            # transacciones hechas por hoy
            transaccionesDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                conteo=Count('fecha'))
            temp_transaccionesDiarias = list(transaccionesDiarias)
            transaccionesDiariasArr = []
            for element in temp_transaccionesDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['conteo'])
                transaccionesDiariasArr.append(aux)
            transaccionesDiariasArr = simplejson.dumps(transaccionesDiariasArr)
            #print(transaccionesDiariasArr)


            # ganancias de hoy
            gananciasDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                ganancia=Sum('precio'))
            temp_gananciasDiarias = list(gananciasDiarias)
            gananciasDiariasArr = []
            for element in temp_gananciasDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['ganancia'])
                # print("AUX")
                # print(aux)
                gananciasDiariasArr.append(aux)
            gananciasDiariasArr = simplejson.dumps(gananciasDiariasArr)
            #print(gananciasDiariasArr)


            # todos los productos del vendedor
            productos = Comida.objects.filter(idVendedor=id).values('nombre', 'precio')
            temp_productos = list(productos)
            productosArr = []
            productosPrecioArr = []
            for element in temp_productos:
                aux = []
                productosArr.append(element['nombre'])
                aux.append(element['nombre'])
                aux.append(element['precio'])
                productosPrecioArr.append(aux)
            productosArr = simplejson.dumps(productosArr)
            productosPrecioArr = simplejson.dumps(productosPrecioArr)
            ##print(productosPrecioArr)

            # productos vendidos hoy con su cantidad respectiva
            fechaHoy = str(timezone.now()).split(' ', 1)[0]
            productosHoy = Transacciones.objects.filter(idVendedor=id,fecha__range=[fini,ffin]).values('nombreComida').annotate(
                conteo=Count('nombreComida'))
            temp_productosHoy = list(productosHoy)
            productosHoyArr = []
            for element in temp_productosHoy:
                aux = []
                aux.append(element['nombreComida'])
                aux.append(element['conteo'])
                productosHoyArr.append(aux)
            productosHoyArr = simplejson.dumps(productosHoyArr)

            print(productosHoyArr)

            fechaini= fini.split("-")
            fechafin=ffin.split("-")
            desde="Desde : "+ fechaini[2]+" / " +fechaini[1]+" / "+ fechaini[0]
            hasta="Hasta : "+ fechafin[2]+" / " +fechafin[1]+" / "+ fechafin[0]
            return render(request, 'main/fijoDashboard.html',
                          {"transacciones": transaccionesDiariasArr, "ganancias": gananciasDiariasArr,
                           "productos": productosArr, "productosHoy": productosHoyArr,
                           "productosPrecio": productosPrecioArr, "Titulo": "Ventas por Rango","desde":desde,"hasta":hasta})

        elif usuario.tipo is 3:  # Vendedor ambulante
            # transacciones hechas por hoy
            transaccionesDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                conteo=Count('fecha'))
            temp_transaccionesDiarias = list(transaccionesDiarias)
            transaccionesDiariasArr = []
            for element in temp_transaccionesDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['conteo'])
                transaccionesDiariasArr.append(aux)
            transaccionesDiariasArr = simplejson.dumps(transaccionesDiariasArr)
            # print(transaccionesDiariasArr)

            # ganancias de hoy
            gananciasDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                ganancia=Sum('precio'))
            temp_gananciasDiarias = list(gananciasDiarias)
            gananciasDiariasArr = []
            for element in temp_gananciasDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['ganancia'])
                # print("AUX")
                # print(aux)
                gananciasDiariasArr.append(aux)
            gananciasDiariasArr = simplejson.dumps(gananciasDiariasArr)
            # print(gananciasDiariasArr)


            # todos los productos del vendedor
            productos = Comida.objects.filter(idVendedor=id).values('nombre', 'precio')
            temp_productos = list(productos)
            productosArr = []
            productosPrecioArr = []
            for element in temp_productos:
                aux = []
                productosArr.append(element['nombre'])
                aux.append(element['nombre'])
                aux.append(element['precio'])
                productosPrecioArr.append(aux)
            productosArr = simplejson.dumps(productosArr)
            productosPrecioArr = simplejson.dumps(productosPrecioArr)
            print(productosPrecioArr)

            # productos vendidos hoy con su cantidad respectiva
            fechaHoy = str(timezone.now()).split(' ', 1)[0]
            productosHoy = Transacciones.objects.filter(idVendedor=id, fecha__range=[fini,ffin]).values('nombreComida').annotate(
                conteo=Count('nombreComida'))
            temp_productosHoy = list(productosHoy)
            productosHoyArr = []
            for element in temp_productosHoy:
                aux = []
                aux.append(element['nombreComida'])
                aux.append(element['conteo'])
                productosHoyArr.append(aux)
            productosHoyArr = simplejson.dumps(productosHoyArr)
            print(fini)
            # print(productosHoyArr)

            fechaini = fini.split("-")
            fechafin = ffin.split("-")
            desde = "Desde : " + fechaini[2] + " / " + fechaini[1] + " / " + fechaini[0]
            hasta = "Hasta : " + fechafin[2] + " / " + fechafin[1] + " / " + fechafin[0]
            return render(request, 'main/ambulanteDashboard.html',
                          {"transacciones": transaccionesDiariasArr, "ganancias": gananciasDiariasArr,
                           "productos": productosArr, "productosHoy": productosHoyArr,
                           "productosPrecio": productosPrecioArr, "Titulo": "Ventas por Rango","desde": desde, "hasta":hasta})

    return redirect('index')  # cae aqui si usuario no esta auntentificado o si no es vendedor

def estadisticasVendedor(request):
    if request.user.is_authenticated():
        usuario = Usuario.objects.get(django_user=request.user)
        id = usuario.id
        if usuario.tipo is 2:  ## Vendedor fijo
            # transacciones hechas por hoy
            transaccionesDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                conteo=Count('fecha'))
            temp_transaccionesDiarias = list(transaccionesDiarias)
            transaccionesDiariasArr = []
            for element in temp_transaccionesDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['conteo'])
                transaccionesDiariasArr.append(aux)
            transaccionesDiariasArr = simplejson.dumps(transaccionesDiariasArr)
            # print(transaccionesDiariasArr)

            # ganancias de hoy
            gananciasDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                ganancia=Sum('precio'))
            temp_gananciasDiarias = list(gananciasDiarias)
            gananciasDiariasArr = []
            for element in temp_gananciasDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['ganancia'])
                # print("AUX")
                # print(aux)
                gananciasDiariasArr.append(aux)
            gananciasDiariasArr = simplejson.dumps(gananciasDiariasArr)
            # print(gananciasDiariasArr)


            # todos los productos del vendedor
            productos = Comida.objects.filter(idVendedor=id).values('nombre', 'precio')
            temp_productos = list(productos)
            productosArr = []
            productosPrecioArr = []
            for element in temp_productos:
                aux = []
                productosArr.append(element['nombre'])
                aux.append(element['nombre'])
                aux.append(element['precio'])
                productosPrecioArr.append(aux)
            productosArr = simplejson.dumps(productosArr)
            productosPrecioArr = simplejson.dumps(productosPrecioArr)

            # productos vendidos hoy con su cantidad respectiva
            fechaHoy = str(timezone.now()).split(' ', 1)[0]
            productosHoy = Transacciones.objects.filter(idVendedor=id, fecha=fechaHoy).values('nombreComida').annotate(
                conteo=Count('nombreComida'))
            temp_productosHoy = list(productosHoy)
            productosHoyArr = []
            for element in temp_productosHoy:
                aux = []
                aux.append(element['nombreComida'])
                aux.append(element['conteo'])
                productosHoyArr.append(aux)
            productosHoyArr = simplejson.dumps(productosHoyArr)
            # print(productosHoyArr)


            return render(request, 'main/fijoDashboard.html',
                          {"transacciones": transaccionesDiariasArr, "ganancias": gananciasDiariasArr,
                           "productos": productosArr, "productosHoy": productosHoyArr,
                           "productosPrecio": productosPrecioArr,"Titulo": "Ventas del Día","desde":"","hasta":""})

        elif usuario.tipo is 3:  # Vendedor ambulante
            # transacciones hechas por hoy
            transaccionesDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                conteo=Count('fecha'))
            temp_transaccionesDiarias = list(transaccionesDiarias)
            transaccionesDiariasArr = []
            for element in temp_transaccionesDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['conteo'])
                transaccionesDiariasArr.append(aux)
            transaccionesDiariasArr = simplejson.dumps(transaccionesDiariasArr)
            # print(transaccionesDiariasArr)

            # ganancias de hoy
            gananciasDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(
                ganancia=Sum('precio'))
            temp_gananciasDiarias = list(gananciasDiarias)
            gananciasDiariasArr = []
            for element in temp_gananciasDiarias:
                aux = []
                aux.append(element['fecha'])
                aux.append(element['ganancia'])
                # print("AUX")
                # print(aux)
                gananciasDiariasArr.append(aux)
            gananciasDiariasArr = simplejson.dumps(gananciasDiariasArr)
            # print(gananciasDiariasArr)


            # todos los productos del vendedor
            productos = Comida.objects.filter(idVendedor=id).values('nombre', 'precio')
            temp_productos = list(productos)
            productosArr = []
            productosPrecioArr = []
            for element in temp_productos:
                aux = []
                productosArr.append(element['nombre'])
                aux.append(element['nombre'])
                aux.append(element['precio'])
                productosPrecioArr.append(aux)
            productosArr = simplejson.dumps(productosArr)
            productosPrecioArr = simplejson.dumps(productosPrecioArr)

            # productos vendidos hoy con su cantidad respectiva
            fechaHoy = str(timezone.now()).split(' ', 1)[0]
            productosHoy = Transacciones.objects.filter(idVendedor=id, fecha=fechaHoy).values('nombreComida').annotate(
                conteo=Count('nombreComida'))
            temp_productosHoy = list(productosHoy)
            productosHoyArr = []
            for element in temp_productosHoy:
                aux = []
                aux.append(element['nombreComida'])
                aux.append(element['conteo'])
                productosHoyArr.append(aux)
            productosHoyArr = simplejson.dumps(productosHoyArr)
            # print(productosHoyArr)

            return render(request, 'main/ambulanteDashboard.html',
                          {"transacciones": transaccionesDiariasArr, "ganancias": gananciasDiariasArr,
                           "productos": productosArr, "productosHoy": productosHoyArr,
                           "productosPrecio": productosPrecioArr,"Titulo": "Ventas del Día","desde":"","hasta":""})

    return redirect('index')  # cae aqui si usuario no esta auntentificado o si no es vendedor

def adminEdit(request):
    nombre = request.POST.get("adminName")
    contraseña = request.POST.get("adminPassword")
    id = request.POST.get("adminId")
    email = request.POST.get("adminEmail")
    avatar = request.POST.get("adminAvatar")
    return render(request, 'main/adminEdit.html',
                  {"nombre": nombre, "contraseña": contraseña, "id": id, "email": email, "avatar": avatar})

def signup(request):
    return render(request, 'main/signup.html', {})

def signupAdmin(request):
    return render(request, 'main/signupAdmin.html', {})

def loggedin(request):
    return render(request, 'main/loggedin.html', {})

def loginAdmin(request):
    id = request.POST.get("userID")
    email = request.POST.get("email")
    avatar = "avatars/" + request.POST.get("fileName")
    nombre = request.POST.get("name")
    contraseña = request.POST.get("password")
    return adminPOST(id, avatar, email, nombre, contraseña, request)

def adminPOST(id, avatar, email, nombre, contraseña, request):
    # ids de todos los usuarios no admins
    datosUsuarios = []
    i = 0
    numeroUsuarios = Usuario.objects.count()
    numeroDeComidas = Comida.objects.count()
    for usr in Usuario.objects.raw('SELECT * FROM usuario WHERE tipo != 0'):
        datosUsuarios.append([])
        datosUsuarios[i].append(usr.id)
        datosUsuarios[i].append(usr.nombre)
        datosUsuarios[i].append(usr.email)
        datosUsuarios[i].append(usr.tipo)
        datosUsuarios[i].append(str(usr.avatar))
        datosUsuarios[i].append(usr.activo)
        datosUsuarios[i].append(usr.formasDePago)
        datosUsuarios[i].append(usr.horarioIni)
        datosUsuarios[i].append(usr.horarioFin)
        datosUsuarios[i].append(usr.contraseña)

        i += 1
    listaDeUsuarios = simplejson.dumps(datosUsuarios, ensure_ascii=False).encode('utf8')
    hola = "hola"
    # print(listaDeUsuarios)

    # limpiar argumentos de salida segun tipo de vista
    argumentos = {"nombre": nombre, "id": id, "avatar": avatar, "email": email, "lista": listaDeUsuarios,
                  "numeroUsuarios": numeroUsuarios, "numeroDeComidas": numeroDeComidas, "contraseña": contraseña}
    return render(request, 'main/baseAdmin.html', argumentos)

def obtenerFavoritos(idVendedor):
    favoritos = 0
    for fila in Favoritos.objects.raw('SELECT * FROM favoritos WHERE idVendedor = "' + str(idVendedor) + '"'):
        favoritos += 1
    return favoritos

def fichaVendedor(request, pkid):
    try:
        vendedor = Usuario.objects.get(id=pkid)
        # obtener alimentos
        i = 0
        listaDeProductos = []
        for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(pkid) + '"'):
            listaDeProductos.append([])
            listaDeProductos[i].append(producto.nombre)
            categoria = str(producto.categorias)
            listaDeProductos[i].append(categoria)
            listaDeProductos[i].append(producto.stock)
            listaDeProductos[i].append(producto.precio)
            listaDeProductos[i].append(producto.descripcion)
            listaDeProductos[i].append(str(producto.imagen))
            i += 1
        listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')

        if vendedor.tipo is not 2 or 3:
            redirect('index')
    except ObjectDoesNotExist:
        redirect('index')

    # Puede ser vista por alumno, vendedor dueño o otro (no autentificado o otro vendedor)
    if request.user.is_authenticated:
        vendedoresJson = sellerList(request,0)
        usuario = Usuario.objects.get(django_user=request.user)
        if str(usuario.id) == str(pkid):  # es el dueño de la ficha,
            if usuario.tipo is 2:  # vendedor fijo

                argumentos = {"nombre": usuario.nombre, "tipo": usuario.tipo, "id": usuario.id,
                              "horarioIni": usuario.horarioIni,
                              "favoritos": obtenerFavoritos(usuario.id), "horarioFin": usuario.horarioFin,
                              "avatar": usuario.avatar,
                              "listaDeProductos": listaDeProductos, "activo": usuario.activo,
                              "formasDePago": usuario.formasDePago,
                              "activo": usuario.activo}
                return render(request, 'main/vendedor-fijo.html', argumentos)

            elif usuario.tipo is 3:  # vendedor ambulante
                argumentos = {"nombre": usuario.nombre, "tipo": usuario.tipo, "id": usuario.id,
                              "avatar": usuario.avatar,
                              "favoritos": obtenerFavoritos(usuario.id), "listaDeProductos": listaDeProductos,
                              "activo": usuario.activo,
                              "formasDePago": usuario.formasDePago}
                return render(request, 'main/vendedor-ambulante.html', argumentos)


        if usuario.tipo is 1:  # vista de alumno
            vendedor = Usuario.objects.get(id=pkid)
            try:
                fav = Favoritos.objects.get(idAlumno=usuario.id, idVendedor=vendedor.id)
                favorito = 1
            except MultipleObjectsReturned:
                # no debería ocurrir pero pasa
                favorito = 1
            except ObjectDoesNotExist:
                favorito = 0
            if vendedor.tipo is 2:
                url = 'main/vendedor-fijo-vistaAlumno.html'
            else:
                url = 'main/vendedor-ambulante-vistaAlumno.html'
            return render(request, url,
                          {"nombre": vendedor.nombre, "nombresesion": usuario.nombre, "tipo": vendedor.tipo,
                           "id": vendedor.id,
                           "avatar": vendedor.avatar, "listaDeProductos": listaDeProductos,
                           "avatarSesion": usuario.avatar,
                           "favorito": favorito, "formasDePago": vendedor.formasDePago,
                           "horarioIni": vendedor.horarioIni,
                           "horarioFin": vendedor.horarioFin, "vendedores":vendedoresJson})

    else:
        # vista de no registrado o otro vendedor
        vendedor = Usuario.objects.get(id=pkid)
        if vendedor.tipo is 2:
            url = 'main/vendedor-fijo-vistaAlumno-sinLogin.html'
        else:
            url = 'main/vendedor-ambulante-vistaAlumno-sinLogin.html'

        return render(request, url,
            {"nombre": vendedor.nombre, "tipo": vendedor.tipo, "id": vendedor.id, "avatar": vendedor.avatar,
            "listaDeProductos": listaDeProductos, "formasDePago": vendedor.formasDePago, "horarioIni": vendedor.horarioIni,
            "horarioFin": vendedor.horarioFin, "activo": vendedor.activo})

def loginReq(request):
    # inicaliar variables
    tipo = 0
    nombre = ''
    url = ''
    id = 0
    horarioIni = 0
    horarioFin = 0
    encontrado = False
    email = request.POST.get("email")
    avatar = ''
    contraseña = ''
    password = request.POST.get("password")
    listaDeProductos = []
    formasDePago = []
    activo = False

    # buscar vendedor en base de datos
    MyLoginForm = LoginForm(request.POST)
    if MyLoginForm.is_valid():
        vendedores = []
        for p in Usuario.objects.raw('SELECT * FROM usuario'):
            if p.contraseña == password and p.email == email:
                tipo = p.tipo
                nombre = p.nombre
                if (tipo == 0):
                    url = 'main/baseAdmin.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    avatar = p.avatar
                    contraseña = p.contraseña
                    break
                elif (tipo == 1):
                    url = 'main/index.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    avatar = p.avatar

                    break
                elif (tipo == 2):
                    url = 'main/vendedor-fijo.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    horarioIni = p.horarioIni
                    horarioFin = p.horarioFin
                    request.session['horarioIni'] = horarioIni
                    request.session['horarioFin'] = horarioFin
                    avatar = p.avatar
                    activo = p.activo
                    formasDePago = p.formasDePago
                    request.session['formasDePago'] = formasDePago
                    request.session['activo'] = activo
                    break
                elif (tipo == 3):
                    url = 'main/vendedor-ambulante.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    avatar = p.avatar
                    activo = p.activo
                    formasDePago = p.formasDePago
                    request.session['formasDePago'] = formasDePago
                    request.session['activo'] = activo
                    break

        # si no se encuentra el usuario, se retorna a pagina de login
        if encontrado == False:
            return render(request, 'main/login.html', {"error": "Usuario o contraseña invalidos"})

        # crear datos de sesion
        request.session['id'] = id
        request.session['tipo'] = tipo
        request.session['email'] = email
        request.session['nombre'] = nombre
        request.session['avatar'] = str(avatar)
        # si son vendedores, crear lista de productos
        for p in Usuario.objects.raw('SELECT * FROM usuario'):
            if p.tipo == 2 or p.tipo == 3:
                vendedores.append(p.id)
        vendedoresJson = simplejson.dumps(vendedores)

        # obtener alimentos en caso de que sea vendedor fijo o ambulante
        if tipo == 2 or tipo == 3:
            i = 0
            for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id) + '"'):
                listaDeProductos.append([])
                listaDeProductos[i].append(producto.nombre)
                categoria = str(producto.categorias)
                listaDeProductos[i].append(categoria)
                listaDeProductos[i].append(producto.stock)
                listaDeProductos[i].append(producto.precio)
                listaDeProductos[i].append(producto.descripcion)
                listaDeProductos[i].append(str(producto.imagen))
                i += 1

        listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')

        # limpiar argumentos de salida segun tipo de vista
        argumentos = {"email": email, "tipo": tipo, "id": id, "vendedores": vendedoresJson, "nombre": nombre,
                      "horarioIni": horarioIni, "horarioFin": horarioFin, "avatar": avatar,
                      "listaDeProductos": listaDeProductos}
        if (tipo == 0):
            request.session['contraseña'] = contraseña
            return adminPOST(id, avatar, email, nombre, contraseña, request)
        if (tipo == 1):
            argumentos = {"nombresesion": nombre, "tipo": tipo, "id": id, "vendedores": vendedoresJson,
                          "avatarSesion": avatar}
        if (tipo == 2):
            request.session['listaDeProductos'] = str(listaDeProductos)
            request.session['favoritos'] = obtenerFavoritos(id)
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "horarioIni": horarioIni,
                          "favoritos": obtenerFavoritos(id), "horarioFin": horarioFin, "avatar": avatar,
                          "listaDeProductos": listaDeProductos, "activo": activo, "formasDePago": formasDePago,
                          "activo": activo}
        if (tipo == 3):
            request.session['listaDeProductos'] = str(listaDeProductos)
            request.session['favoritos'] = obtenerFavoritos(id)
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "avatar": avatar, "favoritos": obtenerFavoritos(id),
                          "listaDeProductos": listaDeProductos, "activo": activo, "formasDePago": formasDePago}

        # enviar a vista respectiva de usuario
        return render(request, url, argumentos)

    # retornar en caso de datos invalidos
    else:
        return render(request, 'main/login.html', {"error": "Usuario o contraseña invalidos"})

def gestionproductos(request):
    return render(request, 'main/agregar-productos.html')

def vendedorprofilepage(request):
    return render(request, 'main/vendedor-profile-page.html', {})

def formView(request):
    if request.session.has_key('id'):
        email = request.session['email']
        tipo = request.session['tipo']
        id = request.session['id']
        if (tipo == 0):
            url = 'main/baseAdmin.html'
        elif (tipo == 1):
            url = 'main/index.html'
        elif (tipo == 2):
            url = 'main/vendedor-fijo.html'
        elif (tipo == 3):
            url = 'main/vendedor-ambulante.html'
        return render(request, url, {"email": email, "tipo": tipo, "id": id})
    else:
        return render(request, 'main/base.html', {})

def logout(request):
    try:
        del request.session['id']
    except:
        pass
    return index(request)

def register(request):
    tipo = request.POST.get("tipo")
    nombre = request.POST.get("nombre")
    email = request.POST.get("email")
    password = request.POST.get("password")
    horaInicial = request.POST.get("horaIni")
    horaFinal = request.POST.get("horaFin")
    avatar = request.FILES.get("avatar")
    formasDePago = []
    if not (request.POST.get("formaDePago0") is None):
        formasDePago.append(request.POST.get("formaDePago0"))
    if not (request.POST.get("formaDePago1") is None):
        formasDePago.append(request.POST.get("formaDePago1"))
    if not (request.POST.get("formaDePago2") is None):
        formasDePago.append(request.POST.get("formaDePago2"))
    if not (request.POST.get("formaDePago3") is None):
        formasDePago.append(request.POST.get("formaDePago3"))

    duser = User.objects.create_user(email,
                                          email,
                                          password)
    authuser = authenticate(username=email, password=password)
    login(request, authuser)

    usuarioNuevo = Usuario(django_user=duser, nombre=nombre, email=email, tipo=tipo, contraseña=password, avatar=avatar,
                           formasDePago=formasDePago, horarioIni=horaInicial, horarioFin=horaFinal)
    usuarioNuevo.save()
    return loginReq(request)

def productoReq(request):
    if request.method == "POST":
        #if request.session.has_key('id'):
        #id = request.session['id']
        user = Usuario.objects.get(django_user=request.user)
        #email = request.session['email']
        #tipo = request.session['tipo']
        email = user.email
        tipo = user.tipo
        if tipo == 3:
            path = "main/baseVAmbulante.html"
            url = "main/vendedor-ambulante.html"
        if tipo == 2:
            path = "main/baseVFijo.html"
            url = "main/vendedor-fijo.html"
        Formulario = GestionProductosForm(request.POST)
        if Formulario.is_valid():
            producto = Comida()
            producto.idVendedor = user.id
            producto.nombre = request.POST.get("nombre")
            producto.imagen = request.FILES.get("comida")
            producto.precio = request.POST.get("precio")
            producto.stock = request.POST.get("stock")
            producto.descripcion = request.POST.get("descripcion")
            producto.categorias = request.POST.get("categoria")
            producto.save()
        else:
            return render(request, 'main/agregar-productos.html',
                              {"path": path, "respuesta": "¡Ingrese todos los datos!"})

        return redirect('fichaVendedor', str(user.id))

@csrf_exempt
def editarVendedor(request):
    if request.user.is_authenticated:
        vendedor = Usuario.objects.get(django_user=request.user)
        if vendedor.tipo < 2 or vendedor.tipo > 3:  # si el usuario autenntificado no es alumno, adios
            return redirect('index')

    id = vendedor.id
    nombre = vendedor.nombre
    formasDePago = vendedor.formasDePago
    avatar = vendedor.avatar
    tipo = vendedor.tipo
    activo = vendedor.activo
    # unused: listaDeProductos = request.session['listaDeProductos']
    # unused: favoritos = request.session['favoritos']
    if (tipo == 2):
        horarioIni = vendedor.horarioIni
        horarioFin = vendedor.horarioFin
        argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "horarioIni": horarioIni, "horarioFin": horarioFin,
                      "avatar": avatar, "activo": activo, "formasDePago": formasDePago}
        url = 'main/editar-vendedor-fijo.html'
    elif (tipo == 3):
        argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "avatar": avatar,
                      "activo": activo, "formasDePago": formasDePago}
        url = 'main/editar-vendedor-ambulante.html'
    return render(request, url, argumentos)

@csrf_exempt
def editarDatos(request):
    id_vendedor = request.POST.get("id_vendedor")
    usuario = Usuario.objects.filter(id=id_vendedor)

    nombre = request.POST.get("nombre")
    tipo = request.POST.get("tipo")

    if (tipo == "2"):
        horaInicial = request.POST.get("horaIni")
        horaFinal = request.POST.get("horaFin")
        if (not (horaInicial is None)):
            usuario.update(horarioIni=horaInicial)
        if (not (horaFinal is None)):
            usuario.update(horarioFin=horaFinal)
            # actualizar vendedores fijos
        for p in Usuario.objects.raw('SELECT * FROM usuario'):
            if p.tipo == 2:
                estado = tiempo(p)
                if estado == "activo":
                    Usuario.objects.filter(nombre=p.nombre).update(activo=1)
                else:
                    Usuario.objects.filter(nombre=p.nombre).update(activo=0)
    avatar = request.FILES.get("avatar")
    formasDePago = ""
    if not (request.POST.get("formaDePago0") is None) and request.POST.get("formaDePago0") != "":
        formasDePago += '0,'
    if not (request.POST.get("formaDePago1") is None) and request.POST.get("formaDePago1") != "":
        formasDePago += '1,'
    if not (request.POST.get("formaDePago2") is None) and request.POST.get("formaDePago2") != "":
        formasDePago += '2,'
    if not (request.POST.get("formaDePago3") is None) and request.POST.get("formaDePago3") != "":
        formasDePago += '3,'

    if (nombre is not None and nombre != ""):
        usuario.update(nombre=nombre)
    if (formasDePago != ""):
        usuario.update(formasDePago=formasDePago[:-1])
    if (avatar is not None and avatar != ""):
        with default_storage.open('../media/avatars/' + str(avatar), 'wb+') as destination:
            for chunk in avatar.chunks():
                destination.write(chunk)
        usuario.update(avatar='/avatars/' + str(avatar))
    return redirigirEditar(id_vendedor, request)

def redirigirEditar(id_vendedor, request):
    for usr in Usuario.objects.raw('SELECT * FROM usuario WHERE id == "' + str(id_vendedor) + '"'):
        id = usr.id
        nombre = usr.nombre
        email = usr.email
        tipo = usr.tipo
        avatar = usr.avatar
        activo = usr.activo
        formasDePago = usr.formasDePago
        horarioIni = usr.horarioIni
        horarioFin = usr.horarioFin
        favoritos = obtenerFavoritos(id_vendedor)

        request.session['id'] = id
        request.session['nombre'] = nombre
        request.session['formasDePago'] = formasDePago
        request.session['avatar'] = str(avatar)
        request.session['tipo'] = tipo
        request.session['activo'] = activo
        request.session['horarioIni'] = horarioIni
        request.session['horarioFin'] = horarioFin
        request.session['favoritos'] = favoritos

        listaDeProductos = []
        i = 0
        url = ''
        argumentos = {}
        for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id_vendedor) + '"'):
            listaDeProductos.append([])
            listaDeProductos[i].append(producto.nombre)
            categoria = str(producto.categorias)
            listaDeProductos[i].append(categoria)
            listaDeProductos[i].append(producto.stock)
            listaDeProductos[i].append(producto.precio)
            listaDeProductos[i].append(producto.descripcion)
            listaDeProductos[i].append(str(producto.imagen))
            i += 1

        listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')
        request.session['listaDeProductos'] = str(listaDeProductos)
        if (tipo == 2):
            url = 'main/vendedor-fijo.html'
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "horarioIni": horarioIni, "horarioFin": horarioFin,
                          "avatar": avatar, "listaDeProductos": listaDeProductos, "activo": activo,
                          "formasDePago": formasDePago, "favoritos": favoritos}
        elif (tipo == 3):
            url = 'main/vendedor-ambulante.html'
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "avatar": avatar,
                          "listaDeProductos": listaDeProductos,
                          "activo": activo, "formasDePago": formasDePago, "favoritos": favoritos}
        return render(request, url, argumentos)

def inicioAlumno(request):
    return index(request)

@csrf_exempt
def borrarProducto(request):
    if request.method == 'GET':
        if request.is_ajax():
            comida = request.GET.get('eliminar')
            Comida.objects.filter(nombre=comida).delete()
            data = {"eliminar": comida}
            return JsonResponse(data)

@csrf_exempt
def editarProducto(request):
    if request.method == 'POST':
        if request.is_ajax():
            form = editarProductosForm(data=request.POST, files=request.FILES)
            nombreOriginal = request.POST.get("nombreOriginal")
            nuevoNombre = request.POST.get('nombre')
            nuevoPrecio = (request.POST.get('precio'))
            nuevoStock = (request.POST.get('stock'))
            nuevaDescripcion = request.POST.get('descripcion')
            nuevaCategoria = (request.POST.get('categoria'))
            nuevaImagen = request.FILES.get("comida")
            if nuevoPrecio != "":
                Comida.objects.filter(nombre=nombreOriginal).update(precio=int(nuevoPrecio))
            if nuevoStock != "":
                Comida.objects.filter(nombre=nombreOriginal).update(stock=int(nuevoStock))
            if nuevaDescripcion != "":
                Comida.objects.filter(nombre=nombreOriginal).update(descripcion=nuevaDescripcion)
            if nuevaCategoria != None:
                Comida.objects.filter(nombre=nombreOriginal).update(categorias=(nuevaCategoria))
            if nuevaImagen != None:
                filename = nombreOriginal + ".jpg"
                with default_storage.open('../media/productos/' + filename, 'wb+') as destination:
                    for chunk in nuevaImagen.chunks():
                        destination.write(chunk)
                Comida.objects.filter(nombre=nombreOriginal).update(imagen='/productos/' + filename)

            if nuevoNombre != "":
                if Comida.objects.filter(nombre=nuevoNombre).exists():
                    data = {"respuesta": "repetido"}
                    return JsonResponse(data)
                else:
                    Comida.objects.filter(nombre=nombreOriginal).update(nombre=nuevoNombre)

            data = {"respuesta": nombreOriginal}
            return JsonResponse(data)

def cambiarFavorito(request):
    if request.user.is_authenticated:
        alumno = Usuario.objects.get(django_user=request.user)
        if alumno.tipo is not 1:  # si el usuario autenntificado no es alumno, adios
            return redirect('index')
    if request.method == "GET":
        if request.is_ajax():
            favorito = request.GET.get('favorito')
            agregar = request.GET.get('agregar')
            if agregar == "si":
                nuevoFavorito = Favoritos()
                nuevoFavorito.idAlumno = alumno.id
                nuevoFavorito.idVendedor = favorito
                nuevoFavorito.save()
                respuesta = {"respuesta": "si"}
            else:
                Favoritos.objects.filter(idAlumno=alumno.id).filter(idVendedor=favorito).delete()
                respuesta = {"respuesta": "no"}
            return JsonResponse(respuesta)

            # return render_to_response('main/baseAdmin.html', {'form':form,'test':test}, context_instance=RequestContext(request))

def cambiarEstado(request):
    if request.user.is_authenticated:
        vendedor = Usuario.objects.get(django_user=request.user)
        if vendedor.tipo is not 3:  # si el usuario autenntificado no es vendedor ambulante, adios
            return redirect('index')
    if request.method == 'GET':
        if request.is_ajax():
            estado = request.GET.get('estado')
            id_vendedor = vendedor.id
            if estado == 'true':
                lat = float(request.GET.get('lat'))
                lng = float(request.GET.get('lng'))
                l = Lugar(lat=lat, lng=lng, usuario=vendedor, acurracy=0)
                l.save()

                Usuario.objects.filter(id=id_vendedor).update(activo=True)
            else:
                Lugar.objects.filter(usuario=vendedor).delete()
                Usuario.objects.filter(id=id_vendedor).update(activo=False)
            data = {"estado": estado}
            return JsonResponse(data)

def cambiarAlert(request):
    if request.user.is_authenticated:
        vendedor = Usuario.objects.get(django_user=request.user)
        if vendedor.tipo is not 3:  # si el usuario autenntificado no es vendedor ambulante, adios
            return redirect('index')
    amb = sellerList(request,1)
    if request.method == 'GET':
        if request.is_ajax():
            alert = request.GET.get('alert')
            if(alert == "false"):
                for i in range(len(amb)):
                    user = Usuario.objects.filter(id=amb[i])
                    user.update(alert=False)
                    print("sacando alerta a " + user[0].nombre)
                id_vendedor = vendedor.id
                Usuario.objects.filter(id=id_vendedor).update(alert=False)
                print("sacando alerta a " + vendedor.nombre)
            data = {"alert": alert}
            return JsonResponse(data)

def notificarCambio(request):
    if request.user.is_authenticated:
        vendedor = Usuario.objects.get(django_user=request.user)
        if vendedor.tipo is not 3:  # si el usuario autenntificado no es vendedor ambulante, adios
            return redirect('index')
        if request.method == 'GET':
            if request.is_ajax():
                id_vendedor = vendedor.id
                user = Usuario.objects.filter(id=id_vendedor)
                data = {"alert": user[0].alert}
                return JsonResponse(data)
    data = {"alert": False}
    return JsonResponse(data)

def dist(x1,y1,x2,y2):
    radT = 6378.0
    lat = ((x1 - x2)*math.pi)/180.0
    long = ((y1 - y2)*math.pi)/180.0
    a = (math.sin(lat/2))**2 + math.cos((x1*math.pi)/180.0)*math.cos((x2*math.pi)/180.0)*((math.sin(long/2))**2)
    c = 2*radT*math.asin(math.sqrt(a))
    return c

def alerta(request):
    amb = sellerList(request,1)
    user_not = Usuario.objects.get(django_user = request.user)
    posicion_user = Lugar.objects.filter(usuario = user_not)
    if request.method == 'GET':
        if request.is_ajax():
            alert = request.GET.get('alert')
            if(alert == "true"):
                for i in range(len(amb)):
                    user = Usuario.objects.filter(id=amb[i])
                    if len(posicion_user) > 0:
                        posicionV = Lugar.objects.filter(usuario = user[0])
                        if len(posicionV) > 0:
                            result = dist(posicion_user[0].lat, posicion_user[0].lng, posicionV[0].lat, posicionV[0].lng)
                            if result <= 15:
                                user.update(alert=True)
                                print("lanzando alerta a " + user[0].nombre)
                    else: # si no esta posicionado -> arroja alerta a todos
                        user.update(alert=True)
                        print("lanzando alerta a " + user[0].nombre)
            data = {"alert": alert}
            return JsonResponse(data)

def editarPerfilAlumno(request):
    if request.user.is_authenticated:
        alumno = Usuario.objects.get(django_user=request.user)
        if alumno.tipo is not 1:  # si el usuario autenntificado no es alumno, adios
            return redirect('index')
    avatar = alumno.avatar
    id = alumno.id
    nombre = alumno.nombre
    favoritos = []
    nombres = []
    for fav in Favoritos.objects.raw("SELECT * FROM Favoritos"):
        if id == fav.idAlumno:
            favoritos.append(fav.idVendedor)
            vendedor = Usuario.objects.filter(id=fav.idVendedor).get()
            nombre = vendedor.nombre
            nombres.append(nombre)
    return render(request, 'main/editar-perfil-alumno.html', {"id": id,
                                                              "avatarSesion": avatar,
                                                              "nombre": nombre,
                                                              "favoritos": favoritos,
                                                              "nombres": nombres})

def procesarPerfilAlumno(request):
    if request.user.is_authenticated:
        alumno = Usuario.objects.get(django_user=request.user)
        if alumno.tipo is not 1:  # si el usuario autenntificado no es alumno, adios
            return redirect('index')
    if request.method == "POST":
        nombreOriginal = alumno.nombre
        nuevoNombre = request.POST.get("nombre")
        count = request.POST.get("switchs")
        aEliminar = []
        nuevaImagen = request.FILES.get("comida")
        for i in range(int(count)):
            fav = request.POST.get("switch" + str(i))
            if fav != "":
                aEliminar.append(fav)

        if nuevoNombre != "":
            if Usuario.objects.filter(nombre=nuevoNombre).exists():
                data = {"respuesta": "repetido"}
                return JsonResponse(data)
            Usuario.objects.filter(nombre=nombreOriginal).update(nombre=nuevoNombre)

        for i in aEliminar:
            for fav in Favoritos.objects.raw("SELECT * FROM Favoritos"):
                if alumno.id == fav.idAlumno:
                    if int(i) == fav.idVendedor:
                        Favoritos.objects.filter(idAlumno=alumno.id).filter(idVendedor=int(i)).delete()
        if nuevaImagen != None:
            filename = nombreOriginal + ".jpg"
            with default_storage.open('../media/avatars/' + filename, 'wb+') as destination:
                for chunk in nuevaImagen.chunks():
                    destination.write(chunk)
            Usuario.objects.filter(id=alumno.id).update(avatar='/avatars/' + filename)

        return JsonResponse({"ejemplo": "correcto"})

@csrf_exempt
def borrarUsuario(request):
    if request.method == 'GET':
        if request.is_ajax():
            uID = request.GET.get('eliminar')
            Usuario.objects.filter(id=uID).delete()
            data = {"eliminar": uID}
            return JsonResponse(data)

@csrf_exempt
def agregarAvatar(request):
    if request.is_ajax() or request.method == 'FILES':
        imagen = request.FILES.get("image")
        nuevaImagen = Imagen(imagen=imagen)
        nuevaImagen.save()
        return HttpResponse("Success")

def editarUsuarioAdmin(request):
    if request.method == 'GET':
        nombre = request.GET.get("name")
        contraseña = request.GET.get('password')
        email = request.GET.get('email')
        avatar = request.GET.get('avatar')
        userID = request.GET.get('userID')

        if (nombre != None):
            print("nombre:" + nombre)
        if (contraseña != None):
            print("contraseña:" + contraseña)
        if (email != None):
            print("email:" + email)
        if (avatar != None):
            print("avatar:" + avatar)
        if (userID != None):
            print("id:" + userID)
        if email != None:
            Usuario.objects.filter(id=userID).update(email=email)
            print("cambio Mail")
        if nombre != None:
            Usuario.objects.filter(id=userID).update(nombre=nombre)
            print("cambio Nombre")
        if contraseña != None:
            Usuario.objects.filter(id=userID).update(contraseña=contraseña)
            print("cambio contraseña")
        if avatar != None:
            Usuario.objects.filter(id=userID).update(avatar=avatar)
            print("cambio avatar")

        data = {"respuesta": userID}
        return JsonResponse(data)

def editarUsuario(request):
    if request.method == 'GET':

        nombre = request.GET.get("name")
        contraseña = request.GET.get('password')
        tipo = request.GET.get('type')
        email = request.GET.get('email')
        avatar = request.GET.get('avatar')
        forma0 = request.GET.get('forma0')
        forma1 = request.GET.get('forma1')
        forma2 = request.GET.get('forma2')
        forma3 = request.GET.get('forma3')
        horaIni = request.GET.get('horaIni')
        horaFin = request.GET.get('horaFin')
        userID = request.GET.get('userID')

        nuevaListaFormasDePago = ""
        if (nombre != None):
            print("nombre:" + nombre)
        if (contraseña != None):
            print("contraseña:" + contraseña)
        if (tipo != None):
            print("tipo:" + tipo)
        if (email != None):
            print("email:" + email)
        if (avatar != None):
            print("avatar:" + avatar)
        if (horaIni != None):
            print("horaIni:" + horaIni)
        if (horaFin != None):
            print("horaFin:" + horaFin)
        if (userID != None):
            print("id:" + userID)
        if (forma0 != None):
            print("forma0:" + forma0)
            nuevaListaFormasDePago += "0"
        if (forma1 != None):
            print("forma1:" + forma1)
            if (len(nuevaListaFormasDePago) != 0):
                nuevaListaFormasDePago += ",1"
            else:
                nuevaListaFormasDePago += "1"
        if (forma2 != None):
            print("forma2:" + forma2)
            if (len(nuevaListaFormasDePago) != 0):
                nuevaListaFormasDePago += ",2"
            else:
                nuevaListaFormasDePago += "2"
        if (forma3 != None):
            print("forma3:" + forma3)
            if (len(nuevaListaFormasDePago) != 0):
                nuevaListaFormasDePago += ",3"
            else:
                nuevaListaFormasDePago += "3"

        litaFormasDePago = (
            (0, 'Efectivo'),
            (1, 'Tarjeta de Crédito'),
            (2, 'Tarjeta de Débito'),
            (3, 'Tarjeta Junaeb'),
        )
        if email != None:
            Usuario.objects.filter(id=userID).update(email=email)
            print("cambio Mail")
        if nombre != None:
            Usuario.objects.filter(id=userID).update(nombre=nombre)
            print("cambio Nombre")
        if contraseña != None:
            Usuario.objects.filter(id=userID).update(contraseña=contraseña)
            print("cambio contraseña")
        if tipo != None:
            Usuario.objects.filter(id=userID).update(tipo=tipo)
            print("cambio tipo")
        if avatar != None:
            Usuario.objects.filter(id=userID).update(avatar=avatar)
            print("cambio avatar")
        if horaIni != None:
            Usuario.objects.filter(id=userID).update(horarioIni=horaIni)
            print("cambio hora ini")
        if horaFin != None:
            Usuario.objects.filter(id=userID).update(horarioFin=horaFin)
            print("cambio hora fin")
        Usuario.objects.filter(id=userID).update(formasDePago=nuevaListaFormasDePago)
        print("cambio formas de pago")

        data = {"respuesta": userID}
        return JsonResponse(data)

def registerAdmin(request):
    tipo = request.POST.get("tipo")
    nombre = request.POST.get("nombre")
    email = request.POST.get("email")
    password = request.POST.get("password")
    horaInicial = request.POST.get("horaIni")
    horaFinal = request.POST.get("horaFin")
    avatar = request.FILES.get("avatar")
    # print(avatar)
    formasDePago = []
    if not (request.POST.get("formaDePago0") is None):
        formasDePago.append(request.POST.get("formaDePago0"))
    if not (request.POST.get("formaDePago1") is None):
        formasDePago.append(request.POST.get("formaDePago1"))
    if not (request.POST.get("formaDePago2") is None):
        formasDePago.append(request.POST.get("formaDePago2"))
    if not (request.POST.get("formaDePago3") is None):
        formasDePago.append(request.POST.get("formaDePago3"))
    usuarioNuevo = Usuario(nombre=nombre, email=email, tipo=tipo, contraseña=password, avatar=avatar,
                           formasDePago=formasDePago, horarioIni=horaInicial, horarioFin=horaFinal)
    usuarioNuevo.save()
    id = request.session['id']
    email = request.session['email']
    avatar = request.session['avatar']
    nombre = request.session['nombre']
    contraseña = request.session['contraseña']
    return adminPOST(id, avatar, email, nombre, contraseña, request)

@csrf_exempt
def verificarEmail(request):
    if request.is_ajax() or request.method == 'POST':
        email = request.POST.get("email")
        if Usuario.objects.filter(email=email).exists():
            data = {"respuesta": "repetido"}
            return JsonResponse(data)
        else:
            data = {"respuesta": "disponible"}
            return JsonResponse(data)

def getStock(request):
    if request.method == "GET":
        stock = request.GET.get("nombre")
        for producto in Comida.objects.raw("SELECT * FROM Comida"):
            if producto.nombre == request.GET.get("nombre"):
                stock = producto.stock
        if request.GET.get("op") == "suma":
            nuevoStock = stock + 1
            Comida.objects.filter(nombre=request.GET.get("nombre")).update(stock=nuevoStock)
        if request.GET.get("op") == "resta":
            nuevoStock = stock - 1
            if stock == 0:
                return JsonResponse({"stock": stock})
            Comida.objects.filter(nombre=request.GET.get("nombre")).update(stock=nuevoStock)
    return JsonResponse({"stock": stock})

def createTransaction(request):
    nombreProducto = request.GET.get("nombre")
    precio = 0
    idVendedor = request.GET.get("idUsuario")
    if Comida.objects.filter(nombre=nombreProducto).exists():
        precio = Comida.objects.filter(nombre=nombreProducto).values('precio')[0]
        listaAux = list(precio.values())
        precio = listaAux[0]
    else:
        return HttpResponse('error message')
    transaccionNueva = Transacciones(idVendedor=idVendedor, precio=precio, nombreComida=nombreProducto)
    transaccionNueva.save()
    return JsonResponse({"transaccion": "realizada"})

def map(request):
    lugares = []
    for lugar in Lugar.objects.raw('SELECT * FROM lugar'):
        if(lugar.usuario.activo):
            lugares.append(lugar)
    return render(request, 'main/index2.html', {'lugares': lugares})

@csrf_exempt
def indexFiltro(request):
    vendedoresJson = sellerList(request, 0)
    categoria = request.POST.get("categoria")

    if request.user.is_authenticated():
        users = Usuario.objects.filter(django_user=request.user)

        f = Favoritos.objects.filter(idAlumno=users[0].id).values_list('idVendedor')
        f_json = json.dumps(list(f), cls=DjangoJSONEncoder)

        if len(users) > 0:
            if users[0].tipo == 2 or users[0].tipo == 3:
                return fichaVendedor(request, users[0].id)
    else:
        f_json = []

    b = Comida.objects.filter().values_list('nombre', 'categorias', 'stock', 'idVendedor')
    vendedoresFiltrados = []
    for comida in b:
        if comida[1][0] == categoria:
            if comida[2] != 0:
                vendedoresFiltrados.append(comida[3])

    lugares = Lugar.objects.filter(usuario__in=vendedoresFiltrados).values_list('lat', 'lng', 'acurracy', 'usuario')
    lugares_json = json.dumps(list(lugares), cls=DjangoJSONEncoder)

    v = Usuario.objects.filter(Q(tipo=2) | Q(tipo=3)).values_list('nombre')
    v_json = json.dumps(list(v), cls=DjangoJSONEncoder)


    return render(request, 'main/index.html',
                  {"vendedores": vendedoresJson, "lugares": lugares_json,
                   "vendedoresNombres": v_json, "favoritos": f_json})