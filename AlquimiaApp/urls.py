from django.urls import path
from .views import  (
    OrganizacionView, crear_usuario, ver_inventario,ver_usuario,editar_usuario,
    UserDelete,Searcher,Login,SignOut,crear_inventario,organizacion_delete,crear_ventas,
    ventas_detalles,actualizar_cantidad,ventas_delete
    )

urlpatterns = [
    # INICIO
    path('', Login , name='Inicio'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('usuarios/lista/', ver_usuario , name='ver_usuario'),
    path('editar/<int:id>',editar_usuario,name='editar'),
    path('UserDelete/<int:id>',UserDelete,name='userDelete'),
    path('Search/',Searcher,name='Search'),
    path('logout/',SignOut, name='logout'),
    
    # ORGANIZACIÓN
    path('Organizacion/', OrganizacionView.as_view(), name='organizacion_view'),
    path('Organizacion/delete/<int:id>',organizacion_delete, name='update'),

    #Bodega
    path('Inventario/', ver_inventario,name='ver_inventario'),
    path('actualizar_cantidad/<int:id>/',actualizar_cantidad, name='actualizar_cantidad'),
    path('Inventario/crear/', crear_inventario,name='crear_inventario'),
    
    #Ventas

    path('Ventas/crear/',crear_ventas, name='crear_ventas'),
    path('Ventas/detalles/',ventas_detalles, name='ventas_detalles'),
    path('Ventas/delete/<int:id>',ventas_delete, name='ventas_delete'),
]
