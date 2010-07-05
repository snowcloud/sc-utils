from iso_country import countries as COUNTRY_CHOICES
ISO_GB = "GB"

def make_google_map_url(address):
    return 'http://maps.google.co.uk/maps?q=%s&sa=X&oi=map&ct=title' % address.replace(' ', '+')

def _has_upper(value):
    for c in value:
        if c.isupper(): return True
    return False


def smart_caps(value):
    def _cap(value):
        _exclude = ('de', 'van', 'von')
        if value in _exclude: return value
        else: return value.capitalize()
        
    if _has_upper(value):
        return value
    else:
        return ' '.join(map(_cap, value.split()))

import decimal

def dec(v):
    return decimal.Decimal(str(v))


