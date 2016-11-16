from django.shortcuts import render, HttpResponse
from call import scrape
from call.models import Politician

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

def add_local_house(zipcode, critter):
    matching = Politician.objects.filter(chamber=Politician.HOUSE, zipcode=zipcode, district_or_class=critter.district)
    if len(matching) == 1:
        return critter._replace(local_phones = matching[0].extra_phones,
                                custom_script = matching[0].script)
    else:
        return critter

def scripts(request):
    zipcode = request.GET['zip']
    reps = list(map(lambda r: add_local_house(zipcode, r), scrape.get_representatives(zipcode)))
    global_reps = Politician.objects.filter(shown_to_all=True, chamber=Politician.HOUSE)
    global_sens = []
    for critter in global_reps:
        critter.rep = filter(lambda r: r.district == critter.district_or_class,
                             scrape.get_representatives(critter.zipcode)).__next__()
    context = {'name': request.GET.get('name', '$NAME'),
               'city': '$CITY',
               'state': '$STATE',
               'senators': [],
               'representatives': reps,
               'global_representatives': global_reps,
               'global_senators': global_sens}

    return render(request, 'call/scripts.html', context)

