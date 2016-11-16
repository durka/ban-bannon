from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import lxml
import re

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
           'Wyoming':        'WY' }


Representative = namedtuple('Representative',
                            ['name', 'party', 'state', 'district'])

SINGLE_REPRESENTATIVE_LOCATION_RE = \
  re.compile(r'(?:At-Large|(\d+)(?:st|nd|th)) Congressional district of ([A-Za-z]+)')

MULTI_REPRESENTATIVES_LOCATION_RE = \
  re.compile(r'([A-Za-z]+) District (\d+)')

def get_representatives(zip):
    response = requests.get('http://ziplook.house.gov/htbin/findrep?ZIP=%s' % zip)
    html     = BeautifulSoup(response.text, 'lxml')
    content  = html.find(id='contentNav')
    one_rep  = content.find(id='RepInfo')
    if one_rep:
        name = one_rep.a
        location_string = content.find('em').find_next_sibling(string=True)
        district, state = SINGLE_REPRESENTATIVE_LOCATION_RE.search(location_string).groups()
        
        return [Representative(
            name     = name.string.strip(),
            party    = name.find_next_sibling(string=True).strip(),
            state    = STATES[state],
            district = int(district) if district else 0
        )]
    else:
        def rep(info):
            name = info.a
            party, location_string = name.find_next_siblings(string=True)
            state, district = MULTI_REPRESENTATIVES_LOCATION_RE.search(location_string).groups()
            
            return Representative(
                name     = name.string.strip(),
                party    = party.strip(),
                state    = STATES[state],
                district = int(district)
            )
        
        return [rep(info) for info in content.find_all(class_='RepInfo')]

