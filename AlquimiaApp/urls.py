from django.urls import path
from .views import  (
    OrganizacionView,EstadisticaView, crear_usuario, ver_inventario,ver_usuario,editar_usuario,
    UserDelete,Login,SignOut,crear_inventario,organizacion_delete,crear_ventas,
    ventas_detalles,actualizar_cantidad,ventas_delete,ventas_detalle,cantidad_ventas,inventario_delete,ventas_detalle_delete,
    editar_bodega,configuracion_user
    )

urlpatterns = [
    # INICIO
    path('', Login , name='Inicio'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('usuarios/lista/', ver_usuario , name='ver_usuario'),
    path('usuarios/configuracion/', configuracion_user , name='configuracion_user'),
    path('editar/<int:id>',editar_usuario,name='editar'),
    path('UserDelete/<int:id>',UserDelete,name='userDelete'),
    path('logout/',SignOut, name='logout'),
    
    # ORGANIZACIÓN
    path('Organizacion/', OrganizacionView.as_view(), name='organizacion_view'),
    path('Organizacion/delete/<int:id>',organizacion_delete, name='update'),

    #Bodega
    path('Inventario/', ver_inventario,name='ver_inventario'),
    path('actualizar_cantidad/<int:id>/',actualizar_cantidad, name='actualizar_cantidad'),
    path('Inventario/crear/', crear_inventario,name='crear_inventario'),
    path('Inventario/delete/<int:id>/', inventario_delete,name='inventarioDelete'),
    path('Inventario/actualizar/<int:id>/',editar_bodega,name='editarInventario'),
    
    #Ventas
    path('Ventas/crear/',crear_ventas, name='crear_ventas'),
    path('cantidad_ventas/<int:id>',cantidad_ventas, name='cantidad_ventas'),
    path('Ventas/delete/<int:id>',ventas_delete, name='ventas_delete'),
    
    # Ventas detalles
    path('Ventas/detalles/',ventas_detalles, name='ventas_detalles'),
    path('Ventas/detalle/',ventas_detalle, name='ventas_detalle'),
    path('Ventas/detalle/delete/<int:id>',ventas_detalle_delete, name='ventas_detalle_delete'),
    
    
    # ORGANIZACIÓN
    path('Estadistica/', EstadisticaView.as_view(), name='estadistica_view'),
    
    
]
