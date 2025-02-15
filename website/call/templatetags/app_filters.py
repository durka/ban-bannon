from django import template
from django.template import Context
from django.template.loader import get_template
from call.models import Position

register = template.Library()

@register.filter
def position_class(position):
    if position == Position.HAS_NOT_SAID:
        return 'has-not-said'
    elif position == Position.SUPPORTS:
        return 'supports'
    elif position == Position.DENOUNCES:
        return 'denounces'
    else:
        return 'unknown-position'

PHONE_TEMPLATE = get_template('call/phone_numbers.html')

@register.filter
def critter_phone(critter, phone):
    return PHONE_TEMPLATE.render(Context({'critter': critter, 'phone': phone}))
