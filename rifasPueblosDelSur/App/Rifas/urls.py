from django.urls import path
from . import views

urlpatterns = [
    path('',views.inicio, name='inicio_rifa'),#lo coloque yo
    path('rifa/<int:id>/', views.detalle_rifa, name='rifa_selec'),#esto name='rifa_selec', es una alias para la url, para utilizarlo de forma mas facil
                                                                 #en el html {% url 'rifa_selec' rifa.id_rifa %} = <a href="/rifa/{{ rifa.id_rifa }}/">
    path('crear_transaccion/', views.crear_transaccion, name='crear_transaccion'),
    path('api/transacciones/<int:ticket_id>/', views.obtener_transacciones_ticket, name='transacciones_ticket')
]