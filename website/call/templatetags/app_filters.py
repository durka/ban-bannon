from django import template
from django.template import Context
from django.template.loader import get_template
from call.models import Politician

register = template.Library()

@register.filter
def position_class(position):
    if position == Politician.HAS_NOT_SAID:
        return 'has-not-said'
    elif position == Politician.SUPPORTS:
        return 'supports'
    elif position == Politician.DENOUNCES:
        return 'denounces'
    else:
        return 'unknown-position'

PHONE_TEMPLATE = get_template('call/phone_number.html')

@register.filter
def critter_phone(critter, phone):
    return PHONE_TEMPLATE.render(Context({'critter': critter, 'phone': phone}))
