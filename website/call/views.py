from collections import namedtuple
from enum import Enum
from itertools import chain
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render, HttpResponse
from call import scrape
from call.models import Politician

def index(request):
    context = {}
    return render(request, 'call/index.html', context)

Phone = namedtuple('Phone',
                   ['number', 'desc'])

Critter = namedtuple('Critter',
                     ['title', 'name', 'last_name',
                      'party', 'state',
                      'phones', 'script'])

def from_scraped(chamber, zip_or_state, critter):
    matching = Politician.objects.get_or_none(chamber=chamber, zip_or_state=zip_or_state, district_or_class=critter.disambig)
    if matching is not None:
        extra_phones = map(lambda p: Phone(number = p.number, desc = p.desc),
                           matching.phone_set.all())
        if matching.script is not None and len(matching.script) > 0:
            script = matching.script
        else:
            script = matching.position
    else:
        extra_phones = []
        script = Politician.HAS_NOT_SAID

    return Critter(title = 'Representative' if chamber == Politician.HOUSE else 'Senator',
                   name = critter.name,
                   last_name = critter.last_name,
                   party = critter.party,
                   state = critter.state,
                   phones = [Phone(number = critter.dc_phone,
                                   desc = None)]
                            + list(extra_phones),
                   script = script)

def from_model(chamber, critter):
    get = scrape.get_representatives if chamber == Politician.HOUSE else scrape.get_senators
    matching = next(filter(lambda r: r.disambig == critter.district_or_class,
                           get(critter.zip_or_state)))

    extra_phones = map(lambda p: Phone(number = p.number, desc = p.desc),
                       critter.phone_set.all())
    if critter.script is not None and len(critter.script) > 0:
        script = critter.script
    else:
        script = critter.position

    return Critter(title = 'Representative' if chamber == Politician.HOUSE else 'Senator',
                   name = matching.name,
                   last_name = matching.last_name,
                   party = matching.party,
                   state = matching.state,
                   phones = [Phone(number = matching.dc_phone,
                                   desc = None)]
                            + list(extra_phones),
                   script = script)

def render_script(critter, context):
    if critter.script == Politician.HAS_NOT_SAID:
        script = get_template('call/scripts/has_not_said.html')
    elif critter.script == Politician.SUPPORTS:
        script = get_template('call/scripts/supports.html')
    elif critter.script == Politician.DENOUNCES:
        script = get_template('call/scripts/denounces.html')
    else:
        script = Template(critter.script)

    context['critter'] = critter

    return script.render(Context(context))

def scripts(request):
    name = request.GET.get('name', '$NAME')
    zipcode = request.GET['zip']

    (city, state) = scrape.zip_code_city_state(zipcode)

    reps = map(lambda r: from_scraped(Politician.HOUSE, zipcode, r),
               scrape.get_representatives(zipcode))
    sens = map(lambda s: from_scraped(Politician.SENATE, state, s),
               scrape.get_senators(state))
    greps = map(lambda r: from_model(Politician.HOUSE, r),
                Politician.objects.filter(shown_to_all=True, chamber=Politician.HOUSE))
    gsens = map(lambda s: from_model(Politician.SENATE, s),
                Politician.objects.filter(shown_to_all=True, chamber=Politician.SENATE))

    critters = chain(map(lambda c: c._replace(script = render_script(c, {'name': name, 'place': city})),
                         chain(reps, sens)),
                     map(lambda c: c._replace(script = render_script(c, {'name': name, 'place': state})),
                         chain(greps, gsens)))

    return render(request, 'call/scripts.html', {'critters': list(critters)})

