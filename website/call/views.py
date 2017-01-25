from website import settings
from collections import namedtuple
from enum import Enum
from itertools import chain
from django.http import Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render, HttpResponse
from call import scrape
from call.constants import STATE_NAMES, THE_STATES
from call.models import Politician, Campaign, Position

def get_campaign(request):
    c = request.GET.get('campaign')
    if c is None and settings.CAMPAIGN_OVERRIDE is not None:
        c = settings.CAMPAIGN_OVERRIDE
    if c == '':
        if 'bannon' in request.get_host():
            c = 'bannon'
        elif 'pruitt' in request.get_host():
            c = 'pruitt'
        elif 'aca' in request.get_host():
            c = 'obamacare'
        else:
            return None
    return Campaign.objects.get(name=c)

def index(request):
    return render_index(request, {})

def render_index(request, extra_values):
    values = {'campaign':  get_campaign(request),
              'campaigns': Campaign.objects.all(),
              'zip':       '',
              'name':      '' }
    values.update(extra_values)
    return render(request, 'call/index.html', values)

Phone = namedtuple('Phone',
                   ['number', 'desc'])

Critter = namedtuple('Critter',
                     ['title', 'name', 'last_name', 'leadership_role',
                      'party', 'state',
                      'phones',
                      'position', 'script'])

def merge_scraped_with_model(scraped_critter, model_pol, positions, campaign):
    if model_pol:
        try:
            model_pos = Position.objects.get(politician=model_pol, campaign__name=campaign)
            script          = model_pos.script          or None
            position        = model_pos.position
        except Position.DoesNotExist:
            script          = None
            position        = None

        extra_phones        = [Phone(number = p.number, desc = p.desc) for p in model_pol.phone_set.all()]
        leadership_role     = model_pol.leadership_role or None
    else:
        extra_phones    = []
        position        = None
        script          = None
        leadership_role = None

    if not position:
        position = Position.DENOUNCES if positions.get(scraped_critter.website, False) else Position.HAS_NOT_SAID
    
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

def from_scraped(zip_or_state, critter, positions, campaign):
    matching = Politician.objects.get_or_none(chamber           = critter.chamber,
                                              zip_or_state      = zip_or_state,
                                              district_or_class = critter.disambig)
    return merge_scraped_with_model(critter, matching, positions, campaign)

def from_model(pol, positions, campaign):
    get = scrape.get_representatives if pol.chamber == Politician.HOUSE else scrape.get_senators
    matching = next(filter(lambda r: r.disambig == pol.district_or_class,
                           get(pol.zip_or_state)))
    return merge_scraped_with_model(matching, pol, positions, campaign)

def render_script(critter, context, campaign):
    if critter.script:
        script = Template(critter.script)
    elif critter.position == Position.HAS_NOT_SAID:
        script = get_template('call/%s/has_not_said.html' % campaign)
    elif critter.position == Position.SUPPORTS:
        script = get_template('call/%s/supports.html' % campaign)
    elif critter.position == Position.DENOUNCES:
        script = get_template('call/%s/denounces.html' % campaign)
    
    context['critter'] = critter
    context['campaign'] = campaign

    return script.render(Context(context))

def scripts(request):
    campaign = get_campaign(request)
    if campaign is None:
        return render_index(request, {
            'zip': request.GET.get('zip', ''),
            'name': request.GET.get('name', ''),
            'error': 'You have to choose an issue'
            })

    name = request.GET.get('name', '$NAME')
    if len(name) == 0:
        name = '$NAME'
    zipcode = request.GET['zip']

    try:
        (city, state) = scrape.zip_code_city_state(zipcode)
    except AttributeError:
        return render_index(request, {
                'zip': zipcode,
                'name': request.GET.get('name', ''),
                'error': 'Invalid zip code %s' % zipcode
                })

    if campaign.checker is None or campaign.checker == '':
        positions = {}
    else:
        positions = getattr(scrape, campaign.checker)(state)

    if campaign.include_senators:
        sens  = (from_scraped(state,   s, positions, campaign) for s in scrape.get_senators(state))
    else:
        sens = []
    gsens = (from_model(s, {}, campaign) for s in Politician.objects.filter(shown_to_all=campaign, chamber=Politician.SENATE))
    greps = (from_model(r, {}, campaign) for r in Politician.objects.filter(shown_to_all=campaign, chamber=Politician.HOUSE))
    if campaign.include_representatives:
        reps  = (from_scraped(zipcode, r, positions, campaign) for r in scrape.get_representatives(zipcode))
    else:
        reps = []

    def render_with(place):
        return lambda c: c._replace(script = render_script(c, {'name': name, 'place': place}, campaign))

    state_name = STATE_NAMES[state]
    if state_name in THE_STATES:
        state_name = 'the %s' % state_name

    good_critters = []
    bad_critters  = []
    for critter in chain(map(render_with(city),       chain(reps, sens)),
                         map(render_with(state_name), chain(greps, gsens))):
        if critter.position == Position.DENOUNCES:
            good_critters.append(critter)
        else:
            bad_critters.append(critter)
    
    return render(request, 'call/scripts.html',
                  { 'campaign':      campaign,
                    'state':         state,
                    'good_critters': good_critters,
                    'bad_critters':  bad_critters })

