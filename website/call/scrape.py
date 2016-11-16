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
                            ['name', 'party', 'state', 'district', 'dc_phone'])

SINGLE_REPRESENTATIVE_LOCATION_RE = \
  re.compile(r'(?:At-Large|(\d+)(?:st|nd|th)) Congressional district of ([A-Za-z]+)')

MULTI_REPRESENTATIVES_LOCATION_RE = \
  re.compile(r'([A-Za-z]+) District (\d+)')

def find_representative_for_zip(zip):
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
            district = int(district) if district else 0,
            dc_phone = None
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
                district = int(district),
                dc_phone = None
            )
        
        return list(map(rep, content.find_all(class_='RepInfo')))

DIGITS_RE = re.compile(r'[0-9]+')

def get_representative_phone_numbers():
    response = requests.get('http://clerk.house.gov/member_info/mcapdir.aspx')
    html     = BeautifulSoup(response.text, 'lxml')

    phones = {}
    for row in html.table.find_all('tr'):
        cols = [td.text for td in row.find_all('td')]
        if len(cols) != 5: continue
        
        name, state, district_str, phone, room = cols
        district_num = re.match(DIGITS_RE, district_str)

        if district_num:
            district = int(district_num.group(0))
        elif district_str == 'At Large':
            district = 0
        else:
            continue
        
        phones[(state, district)] = '202' + phone.replace('-','')
    return phones

def get_representatives(zip):
    phones = get_representative_phone_numbers()
    return [rep._replace(dc_phone = phones[(rep.state, rep.district)])
            for rep in find_representative_for_zip(zip)]
