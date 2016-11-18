from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import lxml
import re
import json
from urllib.parse import urlparse
from itertools import chain
from memoize import memoize
from call.models import Politician

STATES = { 'Alabama':        'AL',
           'Alaska':         'AK',
           'Arizona':        'AZ',
           'Arkansas':       'AR',
           'California':     'CA',
           'Colorado':       'CO',
           'Connecticut':    'CT',
           'Delaware':       'DE',
           'Florida':        'FL',
           'Georgia':        'GA',
           'Hawaii':         'HI',
           'Idaho':          'ID',
           'Illinois':       'IL',
           'Indiana':        'IN',
           'Iowa':           'IA',
           'Kansas':         'KS',
           'Kentucky':       'KY',
           'Louisiana':      'LA',
           'Maine':          'ME',
           'Maryland':       'MD',
           'Massachusetts':  'MA',
           'Michigan':       'MI',
           'Minnesota':      'MN',
           'Mississippi':    'MS',
           'Missouri':       'MO',
           'Montana':        'MT',
           'Nebraska':       'NE',
           'Nevada':         'NV',
           'New Hampshire':  'NH',
           'New Jersey':     'NJ',
           'New Mexico':     'NM',
           'New York':       'NY',
           'North Carolina': 'NC',
           'North Dakota':   'ND',
           'Ohio':           'OH',
           'Oklahoma':       'OK',
           'Oregon':         'OR',
           'Pennsylvania':   'PA',
           'Rhode Island':   'RI',
           'South Carolina': 'SC',
           'South Dakota':   'SD',
           'Tennessee':      'TN',
           'Texas':          'TX',
           'Utah':           'UT',
           'Vermont':        'VT',
           'Virginia':       'VA',
           'Washington':     'WA',
           'West Virginia':  'WV',
           'Wisconsin':      'WI',
           'Wyoming':        'WY',
           'District of Columbia': 'DC',
           'Puerto Rico':    'PR',
           'American Samoa': 'AS',
           'Guam':           'GU',
           'Northern Mariana Islands': 'MP',
           'Virgin Islands': 'VI',
           }

Critter = namedtuple('Critter',
                     ['name', 'last_name',
                      'chamber', 'party', 'state',
                      'disambig', # rep district or senator class
                      'website', 'dc_phone'])

################################################################################
    
def url_soup(url):
    return BeautifulSoup(requests.get(url, headers={'User-Agent': 'Not Mozilla'}).text, 'lxml')

CITY_STATE_RE = re.compile(r'(.+) ([A-Z][A-Z])')

@memoize(timeout=3600)
def zip_code_city_state(zip):
    html = url_soup('https://tools.usps.com/go/ZipLookupResultsAction!input.action?resultMode=2&postalCode=%s' % zip)
    city_str = html.find(id='result-cities').find(class_='std-address').string
    city, state = CITY_STATE_RE.fullmatch(city_str).groups()
    return (city.title(), state)

################################################################################

def parse_comma_name(str):
    components = [s.strip() for s in str.split(',', 2)]
    if len(components) == 3:
        last, first, suffix = components
        full = '%s %s %s' % (first, last, suffix)
    else:
        last, first = components
        full = '%s %s' % (first, last)
    return (full, last)

################################################################################

ExtraRepInfo = namedtuple('ExtraRepInfo', ['last_name', 'dc_phone'])

def add_extra_info(rep, eri):
    return rep._replace(last_name = eri.last_name, dc_phone = eri.dc_phone)

DIGITS_RE = re.compile(r'[0-9]+')

@memoize(timeout=3600)
def get_representative_extra_info():
    html = url_soup('http://clerk.house.gov/member_info/mcapdir.aspx')

    info = {}
    for row in html.table.find_all('tr'):
        cols = [td.text for td in row.find_all('td')]
        if len(cols) != 5: continue
        
        name, state, district_str, phone, room = cols
        district_num = re.match(DIGITS_RE, district_str)
        
        if district_num:
            district = int(district_num.group(0))
        else:
            district = 0
        
        info[(state, district)] = ExtraRepInfo(last_name = parse_comma_name(name)[1],
                                               dc_phone   = '202' + phone.replace('-',''))
    return info

SINGLE_REPRESENTATIVE_LOCATION_RE = \
  re.compile(r'(?:At-Large|(\d+)(?:st|nd|rd|th)) Congressional district of ([A-Za-z ]+)')

MULTI_REPRESENTATIVES_LOCATION_RE = \
  re.compile(r'([A-Za-z ]+) District (\d+)')

@memoize(timeout=3600)
def find_representative_for_zip(zip):
    html    = url_soup('http://ziplook.house.gov/htbin/findrep?ZIP=%s' % zip)
    content = html.find(id='contentNav')
    one_rep = content.find(id='RepInfo')
    if one_rep:
        name = one_rep.a
        location_string = content.find('em').find_next_sibling(string=True)
        district, state = SINGLE_REPRESENTATIVE_LOCATION_RE.search(location_string).groups()
        
        return [Critter(
            name          = name.string.strip(),
            last_name     = None,
            chamber       = Politician.HOUSE,
            party         = name.find_next_sibling(string=True).strip(),
            state         = STATES[state],
            disambig      = int(district) if district else 0,
            dc_phone      = None,
            website       = urlparse(name['href']).netloc
        )]
    else:
        def rep(info):
            name = info.a
            party, location_string = name.find_next_siblings(string=True)
            state, district = MULTI_REPRESENTATIVES_LOCATION_RE.search(location_string).groups()
            state = state.strip()
            
            return Critter(
                name          = name.string.strip(),
                last_name     = None,
                chamber       = Politician.HOUSE,
                party         = party.strip(),
                state         = STATES[state],
                disambig      = int(district),
                dc_phone      = None,
                website       = urlparse(name['href']).netloc
            )
        
        return list(map(rep, content.find_all(class_='RepInfo')))

@memoize(timeout=3600)
def get_representatives(zip):
    info = get_representative_extra_info()
    return [add_extra_info(rep, info[(rep.state, rep.disambig)])
            for rep in find_representative_for_zip(zip)]

################################################################################

SENATOR_AFFILIATION_RE = re.compile(r'\(([A-Z]) - ([A-Z][A-Z])\)')
SENATOR_CLASS_RE       = re.compile(r'Class (I+)')
NON_DIGIT_RE           = re.compile(r'[^0-9]')

PARTY_CHARS = { 'D': 'Democrat',
                'R': 'Republican',
                'I': 'Independent',
                'L': 'Libertarian',
                'G': 'Green' }

@memoize(timeout=3600)
def get_senators(state):
    html = url_soup('http://www.senate.gov/senators/contact/senators_cfm.cfm?State=%s' % state)
    
    senators    = []
    cur_senator = None
    row_index   = 0 # The rows in the table go person, address, phone number, URL, and terminator line
    for row in html.find_all('table')[1].find_all('tr'):
        if row_index == 0:
            person, class_str = row.find_all('td')
            name_link         = person.a
            name, last_name   = parse_comma_name(name_link.text.strip())
            party_char, state = SENATOR_AFFILIATION_RE.search(name_link.find_next_sibling(string=True)).groups()
            class_            = len(SENATOR_CLASS_RE.search(class_str.text).group(1))
            
            
            cur_senator = Critter(
                name          = name,
                last_name     = last_name,
                chamber       = Politician.SENATE,
                party         = PARTY_CHARS.get(party_char, party_char),
                state         = state,
                disambig      = class_,
                dc_phone      = None,
                website       = None
            )
        elif row_index == 1:
            # Address line
            pass
        elif row_index == 2:
            cur_senator = cur_senator._replace(dc_phone = NON_DIGIT_RE.sub('', row.text))
        elif row_index == 3:
            cur_senator = cur_senator._replace(website = urlparse(row.a['href']).netloc)
        elif row_index == 4:
            # Separator/terminator
            senators.append(cur_senator)
            cur_senator = None
        
        row_index = (row_index + 1) % 5
    
    return senators

################################################################################

SHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/111wy-SKScdGOQ8z_ddk3TARvc4-RAXwRL6I6phoLx70/values/%s?key=AIzaSyANbbbSxNMgc5ZCcvdyHEh6yUHwix3qy1g'

@memoize(timeout=3600)
def check_positions(state):
    if state in ['DC', 'PR', 'AS', 'GU', 'MP', 'VI']:
        state = 'Non-Voting Delegates'
    values = json.loads(requests.get(SHEET_URL % state).text)['values']

    senate_start = 0
    for i in range(len(values)):
        if len(values[i]) >= 3 and values[i][2] == 'Senate Delegation':
            senate_start = i
            senate_end = senate_start + values[senate_start:].index([])
            break
    else:
        senate_start = 0
        senate_end = 0

    house_start = 0
    for i in range(len(values)):
        if len(values[i]) >= 3 and values[i][2] == 'House Delegation':
            house_start = i
            house_end = house_start + values[house_start:].index([])
            break
    else:
        house_start = 0
        house_end = 0

    results = {}
    for i in chain(range(senate_start, senate_end), range(house_start, house_end)):
        website = urlparse(values[i][0]).netloc
        try:
            position = values[i][5] == 'Y'
        except IndexError:
            position = False
        results[website] = position
    
    return results

