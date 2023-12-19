from datetime import datetime, date, time
from decimal import Decimal
import json
from django.db.models import Q
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import  AuthenticationForm
from django.db.models import Q
from django.shortcuts import render
from .forms import CalendarioForm, CustomUserCreationForm, InventarioForm
from AlquimiaApp.models import Calendario, DetallesVenta, Inventario, User, Venta 
import sweetify
from datetime import date

from AlquimiaApp import models

fecha_actual = date.today()

#inicio de sesion
def Login(request):
    if request.user.is_authenticated:
        return redirect('/Inventario/')
    else:
        form = AuthenticationForm()
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                sweetify.error(request,f'El usuario o la contraseña ingresada son incorrectas')
            if form.is_valid():
                login(request,user)
                first_name=form.cleaned_data['username']
                sweetify.success(request,f'Bienvenido {first_name} a la aplicación ')
                if request.user.is_administrador:
                    return redirect('Organizacion/')
                if request.user.is_chef:
                    return redirect('usuarios/lista/')
    data = {'form' : form , 'title':'Iniciar Sesión'}
    return render(request, 'Home.html',data)  

def configuracion_user(request):
    if request.user.is_authenticated:
        user_id=request.user.id
        user = User.objects.get(id=user_id)
        form = CustomUserCreationForm(instance=user)
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST, instance=user)
            try:
                form.save()
                first_name = form.cleaned_data['first_name']
                sweetify.success(request, f'Usuario {first_name} ha sido actualizado correctamente')
                return redirect('../usuarios/lista/')
            except Exception as e:
                sweetify.error(request, f'El usuario no se pudo actualizar: {str(e)}')
        data = {'form': form, 'title': 'Configuración de usuario', 'button': 'actualizar','fechaHoy':fecha_actual}
        return render(request, 'Administrador/crear_usuario.html', data)
    else:
        sweetify.error(request, f'Usuario incorrecto')
    return redirect('/')

def SignOut(request):
    logout(request)
    return redirect('/')

#usuarios


def crear_usuario(request):
# if request.user.is_authenticated:
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try: 
                form.save()
                first_name=form.cleaned_data['first_name']
            
                sweetify.success(request, f'Usuario {first_name} ha sido creado correctamente')
                form = CustomUserCreationForm()
                return redirect("../../usuarios/crear/")
            except:
                sweetify.error(request,f'El usuario no se pudo crear') 
    else:
        form=CustomUserCreationForm()
# else:
#     return redirect('/')

    data = {'form' : form , 'title':'Registrar nuevo usuario','button': 'Registrar','fechaHoy':fecha_actual}
    return render(request, 'Administrador/crear_usuario.html',data)

def ver_usuario(request):
    if request.user.is_authenticated:
        users = User.objects.all()
        fecha=users.filter(date_joined = fecha_actual)
        activo = users.filter(is_active='True')
        inactivo = users.filter(is_active='False')
        total_Activo=activo.count()
        total_Inactivo=inactivo.count()
        registro_Total = users.count()
        registro_TotalHoy = fecha.count()
        data = {'users':users,'fechaHoy':fecha_actual,'registroTotal':registro_Total,'registroTotalHoy':registro_TotalHoy,'inactivo':total_Inactivo,'activo':total_Activo}
        return render(request, 'Administrador/lista_usuario.html',data)
    else:
        return redirect('/')
    

  
def editar_usuario(request, id):
    if request.user.is_administrador:
        user = User.objects.get(id=id)
        form = CustomUserCreationForm(instance=user)
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST, instance=user)
            try:
                form.save()
                first_name = form.cleaned_data['first_name']
                sweetify.success(request, f'Usuario {first_name} ha sido actualizado correctamente')
                return redirect('../usuarios/lista/')
            except Exception as e:
                sweetify.error(request, f'El usuario no se pudo actualizar: {str(e)}')
        data = {'form': form, 'title': 'Actualizar usuario', 'button': 'actualizar','fechaHoy':fecha_actual}
        return render(request, 'Administrador/crear_usuario.html', data)
    else:
        sweetify.error(request, f'Usuario incorrecto')
    return redirect('/')

def UserDelete(request, id):
    if request.user.is_authenticated:
        user = User.objects.get(id=id)
        try:
            # user.is_administrador = False
            # user.is_chef = False
            user.delete()
            sweetify.success(request,f'Usuario desactivado exitosamente!')
        except:
            sweetify.error(request, f'El usuario no se pudo desactivar') 
        return redirect('../usuarios/lista/')
    else:
        return redirect('/')


          


# ORGANIZACION

class OrganizacionView(View):
    template_name = 'Organizacion/Organigrama.html'

    def get(self, request,event_id=None):
        if request.user.is_authenticated:
            date = Calendario.objects.all()
            registros_Hoy = date.filter(start_time__date=fecha_actual)
            insumo = Inventario.objects.all()

            form = CalendarioForm()
            registros_Totales = date.count()
            registros_TotalesHoy = registros_Hoy.count()

            porcionesUtilizadasTotal = sum(registro.Porciones for registro in registros_Hoy if registro.Porciones is not None)
            porcionesTotalBodega = sum(item.porciones_disponibles for item in insumo)
       
            producto_PorPrecio = insumo.values('nombre').annotate(porciones_disponibles=insumo.values('porciones_disponibles'))
            producto_PorPrecio = insumo.values('nombre', 'porciones_disponibles')
            data = list(producto_PorPrecio)
            event_data = {}
            if event_id:
                event_data['event_id'] = event_id
                
            context = {
                'date': date,
                'form': form,
                'title': 'Registrar evento',
                'button': 'Registrar',
                'fechaHoy': fecha_actual,
                'porcionesTotal': porcionesTotalBodega,
                'porcionesUtilizadasTotal': porcionesUtilizadasTotal,
                'registrosTotales': registros_Totales,
                'registrosHoy': registros_TotalesHoy,
                'productoPorPrecio': data,
                'event_id': event_id, 
            }

            return render(request, self.template_name, context)
        else:
            return redirect('/')

    def post(self, request):
        if request.user.is_authenticated:
            form = CalendarioForm(request.POST)
            if form.is_valid():
                try:
                    instance = form.save(commit=False)
                    Nombre = instance.productos
                    inventario_Platillo = Inventario.objects.get(nombre=Nombre)
                
                    if inventario_Platillo.porciones_disponibles >= instance.Porciones:
                        cantidadTotal = inventario_Platillo.porciones_disponibles - instance.Porciones
                        inventario_Platillo.porciones_disponibles = cantidadTotal
                        instance = form.save()
                        inventario_Platillo.save()
                        sweetify.success(request, f'El evento {Nombre} ha sido creado correctamente')
                        form = CalendarioForm()
                        return redirect('/Organizacion/') 
                    else:
                        sweetify.error(request, f'No quedan porciones disponibles en bodega')
                        return redirect('/Organizacion/') 
                except Exception as e:
                    sweetify.error(request, f'El evento no se pudo crear {str(e)}')

            date = Calendario.objects.all()
            context = {'date': date, 'form': form, 'title': 'Registrar evento', 'button': 'Registrar', 'fecha_actual': fecha_actual}
            return render(request, self.template_name, context)
        else:
            return redirect('/')
        
def organizacion_delete(request, id):
    if request.user.is_authenticated:
        event = Calendario.objects.get(id=id)
        Nombre = event.productos
        insumo_id = event.productos.id
        inventario_Platillo = Inventario.objects.get(id=insumo_id)
        try:
            inventario_Platillo.porciones_disponibles  += event.Porciones
            inventario_Platillo.save()
            event.delete()
            sweetify.success(request,f'Evento eliminado exitosamente!')

        except:
            sweetify.error(request, f'El evento no se pudo desactivar') 
        return redirect('../../Organizacion/')
    else:
        return redirect('/')


#Inventario
def crear_inventario(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = InventarioForm(request.POST)
            if form.is_valid():
                try:
                    nombre_Platillo = form.cleaned_data['nombre']
                    inventario_Platillo, created = Inventario.objects.get_or_create(
                        nombre=nombre_Platillo,
                    
                        defaults={
                            'descripcion': form.cleaned_data['descripcion'],
                            'precio': form.cleaned_data['precio'],
                            'porciones_disponibles': form.cleaned_data['porciones_disponibles']
                        }
                    )

                    if not created:
                        cantidad_Platillo = form.cleaned_data['porciones_disponibles']
                        precio = form.cleaned_data['precio']
                        cantidad_Total = inventario_Platillo.porciones_disponibles + cantidad_Platillo
                        inventario_Platillo.precio = precio
                        inventario_Platillo.porciones_disponibles = cantidad_Total
                        inventario_Platillo.save()

                    sweetify.success(request, f'El platillo {nombre_Platillo} se registró correctamente')
                    form = InventarioForm()
                    return redirect("../../Inventario/")
                
                except Exception as e:
                    sweetify.error(request, f'El platillo no se pudo crear: {str(e)}') 
        else:
            form = InventarioForm()
    else:
        return redirect('/') 
 
    data = {'form': form, 'title': 'Registrar nuevo platillo', 'button': 'Registrar', 'fechaHoy': fecha_actual}
    return render(request, 'Bodega/agregar_inventario.html', data)



def actualizar_cantidad(request, id):
    if request.method == 'POST':
        insumo = Inventario.objects.get(id=id)
        accion = request.POST.get('accion')
        if accion == 'restar':
            insumo.porciones_disponibles -= 1
        elif accion == 'sumar':
            insumo.porciones_disponibles += 1
        insumo.save()

    return redirect("../../Inventario/")
  
def ver_inventario(request):
    if request.user.is_authenticated:
        insumo = Inventario.objects.all()
        insumos_Total = insumo.count()
        insumos_Hoy = insumo.filter(fecha__date = fecha_actual)
        insumos_Total_Hoy = insumos_Hoy.count()
       
        porcionesTotal = 0
        precioTotal = 0
        productoPorPrecio = Inventario.objects.values('nombre','precio').annotate(cantidad_precio=Sum('porciones_disponibles'))
        productoPorPrecio = productoPorPrecio.values('precio','nombre', 'cantidad_precio')
        dataProduct = list(productoPorPrecio)
        
        for items in dataProduct:
                items['precio'] = float(items['precio'])

        for item in insumo:
            porcionesTotal += item.porciones_disponibles
            precioTotal += item.precio * item.porciones_disponibles
            
        dinero_Total = precioTotal
        data = {'insumo':insumo , 'insumosTotal':insumos_Total,'insumosHoy':insumos_Total_Hoy,
                'fechaHoy':fecha_actual,'porcionesTotal':porcionesTotal,'dineroTotal':dinero_Total,'productoPorPrecio': dataProduct}
        return render(request, 'Bodega/listaInsumo.html',data)
    else:
        return redirect('/')    

def editar_bodega(request,id):
    if request.user.is_administrador:
        insumo = Inventario.objects.get(id=id)
        form = InventarioForm(instance=insumo)
        if request.method == 'POST':
            form = InventarioForm(request.POST, instance=insumo)
            try:
                form.save()
                nombre = form.cleaned_data['nombre']
                sweetify.success(request, f'El platillo {nombre} ha sido actualizado correctamente')
                return redirect('../../')
            except Exception as e:
                sweetify.error(request, f'El platillo no se pudo actualizar: {str(e)}')
        data = {'form': form, 'title': 'Actualizar insumo', 'button': 'actualizar','fechaHoy':fecha_actual}
        return render(request, 'Bodega/agregar_inventario.html', data)
    else:
        sweetify.error(request, f'Usuario incorrecto')
    return redirect('/')
      
def inventario_delete(request, id):
    if request.user.is_authenticated:
        insumo = Inventario.objects.get(id=id)
        # event = Calendario.objects.get(=id)
        try:
            insumo.delete()
            sweetify.success(request,f'Producto eliminado exitosamente!')
        except:
            sweetify.error(request, f'El producto no se pudo desactivar') 
        return redirect("../../Inventario/")
    else:
        return redirect('/')

#Ventas

def cantidad_ventas(request, id):

    if request.method == 'POST':
        evento = Calendario.objects.get(id=id)
        accion = request.POST.get('accion')
        if accion == 'restar':
            evento.Porciones -= 1
        elif accion == 'sumar':
            evento.Porciones += 1
        evento.save()

    return redirect("../../../Ventas/crear/")

def crear_ventas (request):
    events = Calendario.objects.all()
    data = {'events':events,'fechaHoy':fecha_actual}
    return render(request, 'Ventas/ventasCrear.html',data)

def ventas_delete (request,id):
    if request.user.is_authenticated:
        venta = Venta.objects.get(id=id)
        try:
            venta.delete()
            sweetify.success(request,f'Producto eliminado exitosamente!')
        except:
            sweetify.error(request, f'El producto no se pudo desactivar') 
        return redirect("../../Inventario/")
    else:
        return redirect('/')
  

def ventas_detalles(request):
    ventas = Venta.objects.all()
    if request.method == 'POST':
        selected_event_ids = request.POST.getlist('selected_events')
        for event_id in selected_event_ids:
            try:
                platillo = Calendario.objects.get(id=event_id)
                
                if platillo.realizada == "SI":
                    sweetify.error(request, f'Este producto ya se vendio')
   
                else:
                    venta = Venta.objects.create(
                        nombre_vendedor=platillo.nombre,
                        cantidad_vendida=platillo.Porciones,
                        Total=platillo.productos.precio * platillo.Porciones
                    )
                    venta.save()
                    platillo.realizada = "SI"
                    platillo.save()
                    
                    venta_detalles = DetallesVenta.objects.create(
                        venta=venta,
                        calendario=platillo,
                    )
                    venta_detalles.save()
                    sweetify.success(request, f'La venta N° {venta.id} se registró correctamente')

            except Calendario.DoesNotExist:
                sweetify.error(request, f'El evento con ID {event_id} no existe en el calendario')
            except Inventario.DoesNotExist:
                sweetify.error(request, f'No se encontró el inventario para el platillo {platillo.productos.nombre}')
            except Exception as e:
                sweetify.error(request, f'Error al crear la venta: {str(e)}')

        return redirect("../../Ventas/crear/")

    data = {'ventas': ventas,'fechaHoy':fecha_actual}
    return render(request, 'Ventas/ventasCrear.html', data)



def ventas_detalle(request):
    fecha_actual_hoy = datetime.now()
    detalles_ventas = DetallesVenta.objects.all() 
    detalles_agrupados = {}
    total = 0
    total_precio = 0
    total_adicional = 0
    impuesto = Decimal(1.19)
    fecha = fecha_actual_hoy
    TotalDetalles = 0
    detalles_hoy = [] 
    
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            detalles_hoy = DetallesVenta.objects.filter(venta__fecha__date=fecha_str)
        
        except ValueError:
            fecha = datetime.now()
    if request.method == 'GET':
        detalles_hoy = DetallesVenta.objects.filter(venta__fecha__date=fecha.date())

    for detalle in detalles_hoy:
        nombre_producto = detalle.calendario.productos.nombre
        cantidad_actual = detalle.venta.cantidad_vendida
        fecha = detalle.venta.fecha 
        precio_actual = detalle.venta.Total 

        if nombre_producto in detalles_agrupados:
            detalles_agrupados[nombre_producto]['total_cantidad'] += cantidad_actual
            detalles_agrupados[nombre_producto]['total_precio'] += precio_actual
            detalles_agrupados[nombre_producto]['total_por_impuesto'] += precio_actual * impuesto
            detalles_agrupados[nombre_producto]['total_precio_impuesto'] += precio_actual + (precio_actual * impuesto)
        else: 
            detalles_agrupados[nombre_producto] = {
                'total_cantidad': cantidad_actual,
                'total_precio': precio_actual,
                'total_por_impuesto': precio_actual * impuesto,
                'total_precio_impuesto': precio_actual + (precio_actual * impuesto)
            }

    for detalles_venta in detalles_ventas:
        TotalDetalles += detalles_venta.venta.Total
    
    nombre_producto = "No existen productos agregados hoy" 

    for nombre_producto, detalles_agrupados_producto in detalles_agrupados.items():
        total += detalles_agrupados_producto['total_precio_impuesto']
        total_precio += detalles_agrupados_producto['total_precio']
        total_adicional += detalles_agrupados_producto['total_por_impuesto']
        
    data = {
        'ventas': detalles_ventas, 'fechaHoy': fecha_actual_hoy, 'detalles_hoy': detalles_hoy,
        'nombre_producto': nombre_producto, 'impuesto': impuesto, 'detalles_agrupados': detalles_agrupados,
        'total': total, 'fechaHoy':fecha_actual, 'total_precio': total_precio, 'total_adicional': total_adicional,
        'TotalDetalles': TotalDetalles
    }

    return render(request, 'Ventas/detallesVentas.html', data)



def ventas_detalle_delete (request,id):
    detalles = DetallesVenta.objects.get(id=id)
    venta=detalles.venta
    calendario=detalles.calendario
    venta.delete()
    calendario.delete()
    detalles.delete()
    sweetify.success(request, f'El registró se elimino correctamente')
    return redirect("../../../Ventas/detalle/")


#Estadistica
import matplotlib.pyplot as plt
from django.db.models import Count
from django.db.models.functions import TruncMonth

class EstadisticaView(View):
    template_name = 'Estadistica/Estadistica.html'
    def get(self, request,event_id=None):
        if request.user.is_authenticated:
            date = Calendario.objects.all()
            registros_Hoy = date.filter(start_time__date=fecha_actual)
            insumo = Inventario.objects.all()

            form = CalendarioForm()
            registros_Totales = date.count()
            registros_TotalesHoy = registros_Hoy.count()
            

            
            # Obtener ventas totales por mes
            ventas_por_mes = Venta.objects.filter(fecha__year=fecha_actual.year).values('fecha__month').annotate(ventas_totales=Sum('Total'))

            # Convertir resultados a formato JSON
            ventas_por_mes_json = json.dumps(list(ventas_por_mes), default=str)
            
            # Obtener platillos más vendidos
            platillos_mas_vendidos = DetallesVenta.objects.values('calendario__productos__nombre').annotate(cantidad_vendida=Sum('venta__cantidad_vendida')).order_by('-cantidad_vendida')[:5]
            # Obtener platillo más vendido por mes

            porcionesUtilizadasTotal = sum(registro.Porciones for registro in registros_Hoy if registro.Porciones is not None)
            porcionesTotalBodega = sum(item.porciones_disponibles for item in insumo)

            cantidad_usuarios_activos = User.objects.filter(is_active=True).count()
            cantidad_usuarios_inactivos = User.objects.filter(is_active=False).count()
            cantidad_usuarios_totales = User.objects.count()

            total_ventas_hoy = Venta.objects.filter(fecha__date=fecha_actual).aggregate(Sum('Total'))['Total__sum'] or 0
            total_ventas_totales = Venta.objects.aggregate(Sum('Total'))['Total__sum'] or 0
       
            producto_PorPrecio = insumo.values('nombre').annotate(porciones_disponibles=insumo.values('porciones_disponibles'))
            producto_PorPrecio = insumo.values('nombre', 'porciones_disponibles')
            data = list(producto_PorPrecio)
            event_data = {}
            if event_id:
                event_data['event_id'] = event_id
                
            context = {
                'date': date,
                'form': form,
                'title': 'Registrar evento',
                'button': 'Registrar',
                'fechaHoy': fecha_actual,
                'porcionesTotal': porcionesTotalBodega,
                'porcionesUtilizadasTotal': porcionesUtilizadasTotal,
                'registrosTotales': registros_Totales,
                'registrosHoy': registros_TotalesHoy,
                'productoPorPrecio': data,
                'event_id': event_id,
                'cantidad_usuarios_activos': cantidad_usuarios_activos,  # Incluir el conteo de usuarios activos en el contexto
                'cantidad_usuarios_inactivos': cantidad_usuarios_inactivos, 
                'cantidad_usuarios_totales': cantidad_usuarios_totales,
                'total_ventas_hoy': total_ventas_hoy,
                'ventas_por_mes': ventas_por_mes_json,
                'total_ventas_totales': total_ventas_totales,
                'platillos_mas_vendidos': platillos_mas_vendidos,  # Incluir los platillos más vendidos en el contexto

            }

            return render(request, self.template_name, context)
        else:
            return redirect('/')
        



