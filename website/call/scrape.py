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

################################################################################
    
def url_soup(url):
    return BeautifulSoup(requests.get(url, headers={'User-Agent': 'Not Mozilla'}).text, 'lxml')

CITY_STATE_RE = re.compile(r'(.+) ([A-Z][A-Z])')

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

Representative = namedtuple('Representative',
                            ['name', 'last_name',
                             'party', 'state', 'district',
                             'dc_phone', 'local_phones',
                             'custom_script'])

ExtraRepInfo = namedtuple('ExtraRepInfo', ['last_name', 'dc_phone'])

def add_extra_info(rep, eri):
    return rep._replace(last_name = eri.last_name, dc_phone = eri.dc_phone)

DIGITS_RE = re.compile(r'[0-9]+')

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
        elif district_str == 'At Large':
            district = 0
        else:
            continue
        
        info[(state, district)] = ExtraRepInfo(last_name = parse_comma_name(name)[1],
                                               dc_phone   = '202' + phone.replace('-',''))
    return info

SINGLE_REPRESENTATIVE_LOCATION_RE = \
  re.compile(r'(?:At-Large|(\d+)(?:st|nd|th)) Congressional district of ([A-Za-z]+)')

MULTI_REPRESENTATIVES_LOCATION_RE = \
  re.compile(r'([A-Za-z]+) District (\d+)')

def find_representative_for_zip(zip):
    html    = url_soup('http://ziplook.house.gov/htbin/findrep?ZIP=%s' % zip)
    content = html.find(id='contentNav')
    one_rep = content.find(id='RepInfo')
    if one_rep:
        name = one_rep.a
        location_string = content.find('em').find_next_sibling(string=True)
        district, state = SINGLE_REPRESENTATIVE_LOCATION_RE.search(location_string).groups()
        
        return [Representative(
            name          = name.string.strip(),
            last_name     = None,
            party         = name.find_next_sibling(string=True).strip(),
            state         = STATES[state],
            district      = int(district) if district else 0,
            dc_phone      = None,
            local_phones  = [],
            custom_script = None
        )]
    else:
        def rep(info):
            name = info.a
            party, location_string = name.find_next_siblings(string=True)
            state, district = MULTI_REPRESENTATIVES_LOCATION_RE.search(location_string).groups()
            
            return Representative(
                name          = name.string.strip(),
                last_name     = None,
                party         = party.strip(),
                state         = STATES[state],
                district      = int(district),
                dc_phone      = None,
                local_phones  = [],
                custom_script = None
            )
        
        return list(map(rep, content.find_all(class_='RepInfo')))

def get_representatives(zip):
    info = get_representative_extra_info()
    return [add_extra_info(rep, info[(rep.state, rep.district)])
            for rep in find_representative_for_zip(zip)]

################################################################################

Senator = namedtuple('Senator',
                     ['name', 'last_name',
                      'party', 'state', 'class_',
                      'dc_phone', 'local_phones',
                      'custom_script'])

SENATOR_AFFILIATION_RE = re.compile(r'\(([A-Z]) - ([A-Z][A-Z])\)')
SENATOR_CLASS_RE       = re.compile(r'Class (I+)')
NON_DIGIT_RE           = re.compile(r'[^0-9]')

PARTY_CHARS = { 'D': 'Democrat',
                'R': 'Republican',
                'I': 'Independent',
                'L': 'Libertarian',
                'G': 'Green' }

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
            
            
            cur_senator = Senator(
                name          = name,
                last_name     = last_name,
                party         = PARTY_CHARS.get(party_char, party_char),
                state         = state,
                class_        = class_,
                dc_phone      = None,
                local_phones  = [],
                custom_script = None
            )
        elif row_index == 1:
            # Address line
            pass
        elif row_index == 2:
            cur_senator = cur_senator._replace(dc_phone = NON_DIGIT_RE.sub('', row.text))
        elif row_index == 3:
            # Contact
            pass
        elif row_index == 4:
            # Separator/terminator
            senators.append(cur_senator)
            cur_senator = None
        
        row_index = (row_index + 1) % 5
    
    return senators
