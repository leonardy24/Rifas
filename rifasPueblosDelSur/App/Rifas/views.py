from django.shortcuts import render

# Create your views here.
#AQUI ES DONDE INDICAMOS QUE SE CARGUEN NUESTRO HTML DE TEMPLATE

def inicio(request):
        return render(request, 'index.html')