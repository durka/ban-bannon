from django.shortcuts import render, HttpResponse
from call import scrape
from call.models import Politician

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

def add_local_house(zipcode, critter):
    matching = Politician.objects.filter(chamber=Politician.HOUSE, zip_or_state=zipcode, district_or_class=critter.district)
    if len(matching) == 1:
        return critter._replace(local_phones = matching[0].phone_set.all(),
                                custom_script = matching[0].script)
    else:
        return critter

def add_local_senate(state, critter):
    matching = Politician.objects.filter(chamber=Politician.SENATE, zip_or_state=state, district_or_class=critter.class_)
    print('checking %s against %s' % (critter, matching))
    if len(matching) == 1:
        return critter._replace(local_phones = matching[0].phone_set.all(),
                                custom_script = matching[0].script)
    else:
        return critter

def scripts(request):
    zipcode = request.GET['zip']
    (city, state) = scrape.zip_code_city_state(zipcode)
    reps = list(map(lambda r: add_local_house(zipcode, r), scrape.get_representatives(zipcode)))
    sens = list(map(lambda s: add_local_senate(state, s), scrape.get_senators(state)))
    global_reps = Politician.objects.filter(shown_to_all=True, chamber=Politician.HOUSE)
    global_sens = Politician.objects.filter(shown_to_all=True, chamber=Politician.SENATE)
    for critter in global_reps:
        critter.rep = filter(lambda r: r.district == critter.district_or_class,
                             scrape.get_representatives(critter.zip_or_state)).__next__()
    for critter in global_sens:
        critter.rep = filter(lambda r: r.class_ == critter.district_or_class,
                             scrape.get_senators(critter.zip_or_state)).__next__()
        print(critter.rep)
    context = {'name': request.GET.get('name', '$NAME'),
               'city': city,
               'state': state,
               'senators': sens,
               'representatives': reps,
               'global_representatives': global_reps,
               'global_senators': global_sens}

    return render(request, 'call/scripts.html', context)

