from django.contrib import admin
from .models import Comprador, Rifa,Ticket, Transaccion, Vendedor
# Register your models here.

#AQUI PUEDO REGISTRAT MIS MODELOS PARA QUE APAREZCAN EN ADMIN
admin.site.register(Rifa)
admin.site.register(Ticket)
admin.site.register(Vendedor)
admin.site.register(Transaccion)
admin.site.register(Comprador)