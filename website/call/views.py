from django.shortcuts import render, HttpResponse
from call import scrape

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

def scripts(request):
    zipcode = request.POST['zip']
    context = {'name': request.POST.get('name', '$NAME'),
               'city': '$CITY',
               'state': '$STATE',
               'representatives': scrape.get_representatives(zipcode)}
    return render(request, 'call/scripts.html', context)

