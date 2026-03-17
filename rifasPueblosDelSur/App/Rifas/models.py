from decimal import Decimal
from django.db import models

# Create your models here.
#AQUI CREAMOS LAS TABLAS DE BASE DE DATO, DJANGO YA TIENE UN ORM, ENTONCE AQUI LO QUE HACEMOS
#ES CREAR DIRECTAMENTE LAS CLASES QUE SE MAPEARAN EN LA BASE DE DATOS


class Rifa(models.Model):
    id_rifa=models.AutoField(primary_key=True)
    Nom_rifa=models.CharField(max_length=50)
    cant_tickets=models.IntegerField(null=False)
    fecha_creacion=models.DateField(auto_now_add=True)
    estado_rifa=models.CharField(max_length=20)
    fecha_Sorteo=models.DateField(null=False)
    premio=models.CharField(max_length=100,null=False)
    lote_rige=models.CharField(max_length=50,null=False)
    precio_ticket=models.DecimalField(max_digits=10, decimal_places=2,null=False)

    def save(self, *args, **kwargs):

        es_nueva = self._state.adding  # detecta si es creación

        super().save(*args, **kwargs)  # guarda la rifa primero

        if es_nueva:
            tickets = []

            for i in range(1, self.cant_tickets + 1):
                tickets.append(
                    Ticket(
                        id_Rifa=self,
                        numero=i,
                        precio_ticket=self.precio_ticket
                    )
                )

            Ticket.objects.bulk_create(tickets)
    
    def __str__(self):
        return f"Rifa id:{self.id_rifa}"

class Comprador(models.Model):
    id_comprador=models.AutoField(primary_key=True)
    nom_Apellidos_com=models.CharField(max_length=50,null=False)
    cedula=models.IntegerField(null=False)
    telefono=models.IntegerField(null=False)
    direccion=models.CharField(max_length=50,null=False)

    def __str__(self):
        return f"{self.id_comprador} {self.nom_Apellidos_com}"


class Vendedor(models.Model):
    id_vendedor=models.AutoField(primary_key=True)
    nom_Apellidos_vend=models.CharField(max_length=50,null=False)
    telefono=models.IntegerField(null=False)

    def __str__(self):
        return f"{self.id_vendedor} {self.nom_Apellidos_vend}"

class Ticket(models.Model):
    id_Ticket=models.AutoField(primary_key=True)
    id_Rifa=models.ForeignKey('Rifa',on_delete=models.CASCADE, related_name="tickets",null=False)
    numero=models.IntegerField(null=False)
    comprado=models.BooleanField(default=False)
    abonado=models.BooleanField(default=False)
    id_Comprador=models.ForeignKey('Comprador',on_delete=models.SET_NULL, null=True, blank=True )
    id_Vendedor=models.ForeignKey('Vendedor',on_delete=models.SET_NULL, null=True, blank=True )
    precio_ticket=models.DecimalField(max_digits=10, decimal_places=2,null=False)
    total_Pagado=models.DecimalField(max_digits=10, decimal_places=2,null=True) #no estoy muy seguro que se implementaria esto
    deuda=models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def __str__(self):
        return f"Ticket id:{self.id_Ticket} {self.id_Rifa}"


class Transaccion(models.Model):
    id_Trans=models.AutoField(primary_key=True)
    id_Ticket=models.ForeignKey('Ticket',on_delete=models.CASCADE,related_name="trans_ticket")
    id_Vendedor=models.ForeignKey('Vendedor',on_delete=models.SET_NULL, null=True, blank=True,related_name="trans_vendedor")
    id_Comprador=models.ForeignKey('Comprador',on_delete=models.SET_NULL, null=True, blank=True,related_name="trans_comprador")
    monto=models.DecimalField(max_digits=10, decimal_places=2,null=False)
    tipo_Abono=models.CharField(max_length=50,null=False)#abono o pago completo
    fecha_transaccion=models.DateField(auto_now_add=True,null=False)
    metodo_Pago=models.CharField(max_length=50,null=False)


    def save(self, *args, **kwargs):

        # Guarda la transacción primero
        super().save(*args, **kwargs)
        
        # Luego actualiza el Ticket con la información de la venta
        ticket = self.id_Ticket
        
        # Actualiza el comprador del ticket si aún no lo tiene
        if ticket.id_Comprador is None:
            ticket.id_Comprador = self.id_Comprador
        
        # Actualiza vendedor
        ticket.id_Vendedor = self.id_Vendedor
        
        # Actualiza monto pagado y deuda
        if self.tipo_Abono == "pago_completo":
            ticket.total_Pagado = self.monto
            ticket.deuda = 0
            ticket.comprado = True
            ticket.abonado = False
        else:  # Es un abono
            ticket.total_Pagado = (ticket.total_Pagado or 0) + Decimal(self.monto)
            ticket.deuda = ticket.precio_ticket - ticket.total_Pagado
            ticket.abonado = True
            if ticket.deuda <= 0:
                ticket.comprado = True
                ticket.abonado = False
        
        ticket.save()