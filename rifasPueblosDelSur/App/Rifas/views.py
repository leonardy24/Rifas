from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Rifa, Ticket, Comprador, Vendedor, Transaccion
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.db import transaction

# Create your views here.
#AQUI ES DONDE INDICAMOS QUE SE CARGUEN NUESTRO HTML DE TEMPLATE
class CustomLoginForm(AuthenticationForm):
       username=forms.CharField(widget=forms.TextInput(
              attrs={'class':'form-control', 'placeholder': 'Usuario'}),
                label='Usuario'
        )

       password= forms.CharField(widget=forms.PasswordInput(
              attrs={'class':'form-control', 'placeholder':'Contraseña'}),
                label='Contraseña'
        )


@login_required(login_url='/login/')
def inicio(request):

        rifasDBB= Rifa.objects.all()



        return render(request, 'index.html', {
                "Rifas":rifasDBB
        })


@login_required(login_url='/login/')
def detalle_rifa(request, id):
        
        rifa = Rifa.objects.get(id_rifa=id)

        transacciones = Transaccion.objects.filter(
                id_Ticket__id_Rifa=rifa.id_rifa,
                id_Vendedor__isnull=False
        )

        # Monto total por vendedor (o usuario responsable)
        dinero_por_vendedor = (
                transacciones
                .values('id_Vendedor__username')
                .annotate(total=Sum('monto'))
        )

        labels_dinero = []
        data_dinero = []
        dinero_por_usuario = []

        for item in dinero_por_vendedor:
                        label_vendedor = item.get('id_Vendedor__username') or 'Desconocido'
                        labels_dinero.append(label_vendedor)
                        data_dinero.append(float(item['total'] or 0))
                        dinero_por_usuario.append({
                                'label': label_vendedor,
                                'total': float(item['total'] or 0)
                        })

        tickets = Ticket.objects.filter(id_Rifa=rifa.id_rifa)
        vendidos = tickets.filter(comprado=True).count()
        abonados = tickets.filter(abonado=True).count()
        disponibles = tickets.count() - vendidos - abonados
        return render(request, 'detalle_rifa.html', {
                #"rifaDeta":rifa
                "tickets": tickets
                ,"vendidos": vendidos
                ,"abonados": abonados
                ,"disponibles": disponibles
                ,"rifa": rifa
                ,"labels_dinero": labels_dinero
                ,"data_dinero": data_dinero
                ,"dinero_por_usuario": dinero_por_usuario
        })


@login_required(login_url='/login/')
def crear_transaccion(request):

        #tengo dos tipos de implementaciones, tanto en el metodo de guardas de models.py,
        #como aqui en la vista, pero quiero tener todo centralizado en un solo lugar, exactamente aqui.

        
        if request.method == 'POST':

                with transaction.atomic():

                        modal = request.POST.get('tipo_transaccion')  # 'abono' o 'venta'
                        print("TIPO DE TRANSACCION: ", modal)
                        # Obtener el ticket
                        #ticket = Ticket.objects.get(id_Ticket=request.POST.get('id_ticket'))

                        #bloqueamos el ticket para nadie mas puede modificarlo
                        ticket = Ticket.objects.select_for_update().get(id_Ticket=request.POST.get('id_ticket'))

                        if ticket.comprado:
                               return JsonResponse({
                                      "error": "ticket vendido"
                               },status=400)

                        if modal=='abono':
                        
                                print("ENTRO AL ABONO MODAL")

                                try:
                                        monto = Decimal(request.POST.get('monto'))

                                        if ticket.total_Pagado + monto == ticket.precio_ticket:
                                        
                                                #Es un pago completo

                                                Transaccion.objects.create(
                                                        id_Comprador= ticket.id_Comprador, #Obtenemos el comprador del ticket, ya que el abono se hace sobre un ticket que ya tiene comprador asignado
                                                        id_Vendedor=request.user, #ID DEL VENDEDOR FIJO,
                                                        id_Ticket=ticket,
                                                        monto=request.POST.get('monto'),
                                                        metodo_Pago=request.POST.get('tipo_pago'),
                                                        tipo_Abono="completo")
                        

                                                ticket.comprado = True
                                                ticket.abonado = False
                                                ticket.total_Pagado += monto
                                                ticket.deuda = 0
                                
                                        else : #Es un abono

                                                Transaccion.objects.create(
                                                        id_Comprador= ticket.id_Comprador, #Obtenemos el comprador del ticket, ya que el abono se hace sobre un ticket que ya tiene comprador asignado
                                                        id_Vendedor=request.user, #ID DEL VENDEDOR FIJO,
                                                        id_Ticket=ticket,
                                                        monto=request.POST.get('monto'),
                                                        metodo_Pago=request.POST.get('tipo_pago'),
                                                        tipo_Abono="abono")
                                        
                                                ticket.comprado = False
                                                ticket.abonado = True
                                                ticket.total_Pagado += monto
                                                ticket.deuda = ticket.precio_ticket - ticket.total_Pagado


                                        ticket.save()

                                        return JsonResponse({'status': 'success'}, status=200)
                        
                                except Ticket.DoesNotExist:
                                        return JsonResponse({'error': 'Ticket no encontrado'}, status=404)
                                except Exception as e:
                                        print("ERROR: ", str(e))
                                        return JsonResponse({'error': str(e)}, status=500)
                        

                        elif modal=='venta':
                        
                                try:
                              
                                        print("ENTRO AL VENTA MODAL")

                                        # Si el comprador no existe se crea uno nuevo, si existe se obtiene el existente
                                        comprador, creado = Comprador.objects.get_or_create(
                                        cedula=request.POST.get('cedula'),
                                        defaults={
                                        'nom_Apellidos_com': request.POST.get('nombres_apellidos'),
                                        'telefono': request.POST.get('telefono'),
                                        'direccion': request.POST.get('direccion')
                                        }   
                                        )

                                        monto = float(request.POST.get('monto'))
                                        tipoAbono= ""

                                        if monto == ticket.precio_ticket:
                                                tipoAbono= "completo"
                                        else:
                                                tipoAbono= "abono"

                                        #primero guardo la transaccion, y luego actualizo el estado del ticket.
                                        Transaccion.objects.create(
                                                id_Comprador= comprador,
                                                id_Vendedor=request.user, #ID DEL VENDEDOR FIJO,
                                                id_Ticket=ticket,
                                                monto=request.POST.get('monto'),
                                                metodo_Pago=request.POST.get('tipo_pago'),
                                                tipo_Abono=tipoAbono)
                        
                                        # Actualizamos el comprador del ticket
                                        ticket.id_Comprador = comprador

                                        #Actualizamos el vendedor del ticket
                                        ticket.id_Vendedor = request.user

                                        if tipoAbono == "completo":
                                                # Si el monto es igual al precio del ticket, marcarlo como comprado
                                                ticket.comprado = True
                                                ticket.abonado = False
                                                ticket.total_Pagado = monto
                                                ticket.deuda = 0 
                                        else: # Es un abono
                                                ticket.comprado = False
                                                ticket.abonado = True
                                                ticket.total_Pagado = monto
                                                ticket.deuda = ticket.precio_ticket - Decimal(monto)

                                        ticket.save()
                        
                                        return JsonResponse({'status': 'success'}, status=200)
                        
                                except Ticket.DoesNotExist:
                                        return JsonResponse({'error': 'Ticket no encontrado'}, status=404)
                                except Exception as e:
                                        print("ERROR: ", str(e))
                                        return JsonResponse({'error': str(e)}, status=500)

        return HttpResponse(status=500)
        


@login_required(login_url='/login/')
def obtener_transacciones_ticket(request, ticket_id):
    """Vista API para obtener las transacciones de un ticket específico"""
    try:
        ticket = Ticket.objects.get(id_Ticket=ticket_id)
        transacciones = Transaccion.objects.filter(id_Ticket=ticket).order_by('-fecha_transaccion')
        
        data = []
        for trans in transacciones:
            data.append({
                'id': trans.id_Trans,
                'fecha': trans.fecha_transaccion.strftime('%d/%m/%Y'),
                'monto': str(trans.monto),
                'tipo_abono': trans.tipo_Abono,
                'metodo_pago': trans.metodo_Pago,
                'vendedor': trans.id_Vendedor.username
            })
        
        return JsonResponse(data, safe=False)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def crear_rifa(request):
    if request.method == 'POST':
        

        try:
                Rifa.objects.create(
                        Nom_rifa=request.POST.get('Nom_rifa'),
                        cant_tickets=int(request.POST.get('cant_tickets')),
                        fecha_Sorteo=request.POST.get('fecha_Sorteo'),
                        premio=request.POST.get('premio'),
                        lote_rige=request.POST.get('lote_rige'),
                        precio_ticket=request.POST.get('precio_ticket'),
                        estado_rifa=request.POST.get('estado_rifa')
                )
                

               
                return JsonResponse({'status': 'success'}, status=200)
                
        except Exception as e:
            
                return JsonResponse({'error': str(e)}, status=500)
            
    return render(request, 'crear_rifa.html')          


                
