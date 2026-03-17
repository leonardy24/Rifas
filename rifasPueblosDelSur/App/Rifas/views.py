from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Rifa, Ticket, Comprador, Vendedor, Transaccion
# Create your views here.
#AQUI ES DONDE INDICAMOS QUE SE CARGUEN NUESTRO HTML DE TEMPLATE

def inicio(request):

        rifasDBB= Rifa.objects.all()



        return render(request, 'index.html', {
                "Rifas":rifasDBB
        })


def detalle_rifa(request, id):
        
        rifa = Rifa.objects.get(id_rifa=id)

        #tickets = range(1, rifa.cant_tickets + 1)

        tickets = Ticket.objects.filter(id_Rifa=rifa.id_rifa)
        return render(request, 'detalle_rifa.html', {
                #"rifaDeta":rifa
                "tickets": tickets
        })

def crear_transaccion(request):
        
        if request.method == 'POST':
                
                # Obtener el ticket
                ticket = Ticket.objects.get(id_Ticket=request.POST.get('id_ticket'))
                
                # Si es un abono (no se pasan datos del comprador), usar el comprador existente
                if not request.POST.get('cedula'):
                    comprador = ticket.id_Comprador
                else:
                    # Crear o obtener comprador para nueva venta
                    comprador, creado = Comprador.objects.get_or_create(
                            cedula=request.POST.get('cedula'),
                            defaults={
                                    'nom_Apellidos_com': request.POST.get('nombres_apellidos'),
                                    'telefono': request.POST.get('telefono'),
                                    'direccion': request.POST.get('direccion')
                            }
                    )

                #DE MOMENTO VOY A DEJAR EL VENDEDOR FIJO, PERO LUEGO DIRECTAMENT
                #SELECCIONARMO EL ID DEL VENDEDOR DEL USUARIO LOGUEADO
                print(comprador.id_comprador)
                Transaccion.objects.create(
                        id_Comprador= comprador,
                        id_Vendedor=Vendedor.objects.get(id_vendedor=1), #ID DEL VENDEDOR FIJO,
                        id_Ticket=ticket,
                        monto=request.POST.get('monto'),
                        metodo_Pago=request.POST.get('tipo_pago'),
                        tipo_Abono=request.POST.get('tipo_abono'))
                


        return redirect('inicio_rifa')


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
                'vendedor': trans.id_Vendedor.nom_Apellidos_vend if trans.id_Vendedor else 'N/A'
            })
        
        return JsonResponse(data, safe=False)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

          


                
