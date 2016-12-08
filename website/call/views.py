from collections import namedtuple
from enum import Enum
from itertools import chain
from django.http import Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render, HttpResponse
from call import scrape
from call.constants import STATE_NAMES
from call.models import Politician

def get_campaign(request):
    if 'bannon' in request.get_host():
        return 'bannon'
    elif 'pruitt' in request.get_host():
        return 'pruitt'
    else:
        raise Http404("Campaign not found")

def index(request):
    campaign = get_campaign(request)

    return render(request, 'call/index.html', {'campaign': campaign, 'zip': '', 'name': ''})

Phone = namedtuple('Phone',
                   ['number', 'desc'])

Critter = namedtuple('Critter',
                     ['title', 'name', 'last_name', 'leadership_role',
                      'party', 'state',
                      'phones',
                      'position', 'script'])

def merge_scraped_with_model(scraped_critter, model_pol, positions):
    if model_pol:
        extra_phones    = [Phone(number = p.number, desc = p.desc) for p in model_pol.phone_set.all()]
        position        = model_pol.position
        script          = model_pol.script          or None
        leadership_role = model_pol.leadership_role or None
    else:
        extra_phones    = []
        position        = None
        script          = None
        leadership_role = None

    if not position:
        position = Politician.DENOUNCES if positions.get(scraped_critter.website, False) else Politician.HAS_NOT_SAID
    
    title  = 'Representative' if scraped_critter.chamber == Politician.HOUSE else 'Senator'
    phones = [Phone(number = scraped_critter.dc_phone, desc = 'DC office')] + extra_phones
    
    return Critter(title           = title,
                   name            = scraped_critter.name,
                   last_name       = scraped_critter.last_name,
                   leadership_role = leadership_role,
                   party           = scraped_critter.party,
                   state           = scraped_critter.state,
                   phones          = phones,
                   position        = position,
                   script          = script)

def from_scraped(zip_or_state, critter, positions):
    matching = Politician.objects.get_or_none(chamber           = critter.chamber,
                                              zip_or_state      = zip_or_state,
                                              district_or_class = critter.disambig)
    return merge_scraped_with_model(critter, matching, positions)

def from_model(pol, positions):
    get = scrape.get_representatives if pol.chamber == Politician.HOUSE else scrape.get_senators
    matching = next(filter(lambda r: r.disambig == pol.district_or_class,
                           get(pol.zip_or_state)))
    return merge_scraped_with_model(matching, pol, positions)

def render_script(critter, context, campaign):
    # TODO change DB so multiple campaigns can have custom scripts
    if campaign == 'bannon':
        if critter.script:
            script = Template(critter.script)
        elif critter.position == Politician.HAS_NOT_SAID:
            script = get_template('call/%s/has_not_said.html' % campaign)
        elif critter.position == Politician.SUPPORTS:
            script = get_template('call/%s/supports.html' % campaign)
        elif critter.position == Politician.DENOUNCES:
            script = get_template('call/%s/denounces.html' % campaign)
    else:
        script = get_template('call/%s/has_not_said.html' % campaign)
    
    context['critter'] = critter

    return script.render(Context(context))

def scripts(request):
    campaign = get_campaign(request)

    name = request.GET.get('name', '$NAME')
    if len(name) == 0:
        name = '$NAME'
    zipcode = request.GET['zip']

    try:
        (city, state) = scrape.zip_code_city_state(zipcode)
    except AttributeError:
        return render(request, 'call/index.html', {'campaign': campaign,
                                                   'zip': zipcode,
                                                   'name': request.GET.get('name', ''),
                                                   'error': 'Invalid zip code %s' % zipcode})

    if campaign == 'bannon':
        positions = scrape.check_positions(state)
    else:
        positions = {}

    reps  = (from_scraped(zipcode, r, positions) for r in scrape.get_representatives(zipcode))
    sens  = (from_scraped(state,   s, positions) for s in scrape.get_senators(state))
    greps = (from_model(r, {}) for r in Politician.objects.filter(shown_to_all=True, chamber=Politician.HOUSE))
    gsens = (from_model(s, {}) for s in Politician.objects.filter(shown_to_all=True, chamber=Politician.SENATE))

    def render_with(place):
        return lambda c: c._replace(script = render_script(c, {'name': name, 'place': place}, campaign))

    good_critters = []
    bad_critters  = []
    for critter in chain(map(render_with(city),               chain(reps, sens)),
                         map(render_with(STATE_NAMES[state]), chain(greps, gsens))):
        if critter.position == Politician.DENOUNCES:
            good_critters.append(critter)
        else:
            bad_critters.append(critter)
    
    return render(request, 'call/scripts.html',
                  { 'campaign':      campaign,
                    'good_critters': good_critters,
                    'bad_critters':  bad_critters })

