from django.shortcuts import render, HttpResponse
from call import scrape
from call.models import Politician

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

def scripts(request):
    zipcode = request.GET['zip']
    context = {'name': request.GET.get('name', '$NAME'),
               'city': '$CITY',
               'state': '$STATE',
               'senators': [],
               'representatives': scrape.get_representatives(zipcode),
               'global_representatives': Politician.objects.filter(shown_to_all=True, chamber=Politician.HOUSE),
               'global_senators': Politician.objects.filter(shown_to_all=True, chamber=Politician.SENATE)}

    return render(request, 'call/scripts.html', context)

