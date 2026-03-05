from django.db import models

# Create your models here.
#AQUI CREAMOS LAS TABLAS DE BASE DE DATO, DJANGO YA TIENE UN ORM, ENTONCE AQUI LO QUE HACEMOS
#ES CREAR DIRECTAMENTE LAS CLASES QUE SE MAPEARAN EN LA BASE DE DATOS


class Rifa(models.Model):
    id_rifa=models.AutoField(primary_key=True)
    Nom_rifa=models.CharField(max_length=50)
    cant_tickets=models.IntegerField(null=False)
    fecha_creacion=models.DateField(auto_now_add=True)
    estado=models.CharField(max_length=20)