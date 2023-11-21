
from datetime import datetime, date, time
from django.db.models import Q
from django.db.models import Sum
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

fecha_actual = date.today()

#inicio de sesion
def Login(request):
    if request.user.is_authenticated:
        if request.user.is_administrador:
            return redirect('/Organizacion/')
        if request.user.is_chef:
            return redirect('usuarios/lista/')

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
        totalActivo=activo.count()
        totalInactivo=inactivo.count()
        registroTotal = users.count()
        registroTotalHoy = fecha.count()
        data = {'users':users,'fechaHoy':fecha_actual,'registroTotal':registroTotal,'registroTotalHoy':registroTotalHoy,'inactivo':totalInactivo,'activo':totalActivo}
        return render(request, 'Administrador/lista_usuario.html',data)
    else:
        return redirect('/')
    
def Searcher(request):
    if request.user.is_authenticated:
        search = request.GET['busemp']
        users = User.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) 
                                | Q(date_joined__icontains=search) | Q(username__icontains=search)
                                | Q(is_administrador__icontains=search) | Q(is_chef__icontains=search))
        data={'users':users}
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
                print(str(e))  # Imprime el error para depuración
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
            registrosHoy = date.filter(start_time__date=fecha_actual)
            insumo = Inventario.objects.all()

            form = CalendarioForm()
            registrosTotales = date.count()
            registrosTotalesHoy = registrosHoy.count()

            porcionesUtilizadasTotal = sum(registro.Porciones for registro in registrosHoy if registro.Porciones is not None)
            porcionesTotalBodega = sum(item.porciones_disponibles for item in insumo)
       
            productoPorPrecio = insumo.values('nombre').annotate(porciones_disponibles=insumo.values('porciones_disponibles'))
            productoPorPrecio = insumo.values('nombre', 'porciones_disponibles')
            data = list(productoPorPrecio)
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
                'registrosTotales': registrosTotales,
                'registrosHoy': registrosTotalesHoy,
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
                    instance = form.save()
                    Nombre = instance.nombre
                    sweetify.success(request, f'El evento {Nombre} ha sido creado correctamente')
                    form = CalendarioForm()
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
        try:
            # user.is_administrador = False
            # user.is_chef = False
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
                    nombrePlatillo = form.cleaned_data['nombre']
                    inventarioPlatillo, created = Inventario.objects.get_or_create(
                        nombre=nombrePlatillo,
                    
                        defaults={
                            'descripcion': form.cleaned_data['descripcion'],
                            'precio': form.cleaned_data['precio'],
                            'porciones_disponibles': form.cleaned_data['porciones_disponibles']
                        }
                    )

                    if not created:
                        cantidadPlatillo = form.cleaned_data['porciones_disponibles']
                        cantidadTotal = inventarioPlatillo.porciones_disponibles + cantidadPlatillo
                        inventarioPlatillo.porciones_disponibles = cantidadTotal
                        inventarioPlatillo.save()

                    sweetify.success(request, f'El insumo {nombrePlatillo} se registró correctamente')
                    form = InventarioForm()
                    return redirect("../../Inventario/")
                
                except Exception as e:
                    sweetify.error(request, f'El insumo no se pudo crear: {str(e)}') 
        else:
            form = InventarioForm()
    else:
        return redirect('/') 

    data = {'form': form, 'title': 'Registrar nuevo platillo', 'button': 'Registrar', 'fechaHoy': fecha_actual}
    return render(request, 'Bodega/Agregarinventario.html', data)

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
        insumosTotal = insumo.count()
        insumosHoy = insumo.filter(fecha__date = fecha_actual)
        insumosTotalHoy = insumosHoy.count()
       
        porcionesTotal = 0
        precioTotal = 0
        productoPorPrecio = Inventario.objects.values('nombre','precio').annotate(cantidad_precio=Sum('porciones_disponibles'))
        productoPorPrecio = productoPorPrecio.values('precio','nombre', 'cantidad_precio')
        dataProduct = list(productoPorPrecio)
        
        for items in dataProduct:
                items['precio'] = float(items['precio'])

        for item in insumo:
            porcionesTotal += item.porciones_disponibles
            precioTotal += item.precio 
            
        dineroTotal = porcionesTotal * precioTotal
        data = {'insumo':insumo , 'insumosTotal':insumosTotal,'insumosHoy':insumosTotalHoy,
                'fechaHoy':fecha_actual,'porcionesTotal':porcionesTotal,'dineroTotal':dineroTotal,'productoPorPrecio': dataProduct}
        return render(request, 'Bodega/listaInsumo.html',data)
    else:
        return redirect('/')    
    
    
def crear_ventas (request):
    events = Calendario.objects.all()
    data = {'events':events}
    return render(request, 'Ventas/ventasCrear.html',data)

def ventas_detalles(request):
    ventas = Venta.objects.all()

    if request.method == 'POST':
        selected_event_ids = request.POST.getlist('selected_events')

        for event_id in selected_event_ids:
            try:
                platillo = Calendario.objects.get(id=event_id)
                print(platillo.nombre)
                venta = Venta.objects.create(
                    nombre_vendedor=platillo.nombre,
                    cantidad_vendida=platillo.Porciones,
                    Total=platillo.productos.precio * platillo.Porciones
                )
                venta.productos.set([platillo]) 
                platillo.realizada = "SI"
                platillo.save()

                inventarioPlatillo = Inventario.objects.get(nombre=platillo.productos.nombre)

                if inventarioPlatillo.porciones_disponibles > 0:
                    cantidadTotal = inventarioPlatillo.porciones_disponibles - venta.cantidad_vendida
                    inventarioPlatillo.porciones_disponibles = cantidadTotal
                    inventarioPlatillo.save()
                    sweetify.success(request, f'La venta N° {venta.id} se registró correctamente')
                else:
                    sweetify.error(request, f'No quedan porciones disponibles en bodega')
                    inventarioPlatillo.delete()
                    inventarioPlatillo.save()
                    
                    
            except Calendario.DoesNotExist:
                sweetify.error(request, f'El evento con ID {event_id} no existe en el calendario')
            except Inventario.DoesNotExist:
                sweetify.error(request, f'No se encontró el inventario para el platillo {platillo.productos.nombre}')
            except Exception as e:
                sweetify.error(request, f'Error al crear la venta: {str(e)}')

        return redirect("../../Ventas/crear/")

    data = {'ventas': ventas}
    return render(request, 'Ventas/ventasCrear.html', data)


def ventas_detalles (request):
    ventas = DetallesVenta.objects.all()
    
    data = {'ventas':ventas,
            'fechaHoy':fecha_actual
            }
    return render(request, 'Ventas/detallesVentas.html',data)

def ventas_delete (request,id):
    platillo = Calendario.objects.get(id=id)
    platillo.delete()
    platillo.save()
    return redirect("../../Ventas/crear/")
