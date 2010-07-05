from django import template
from django.conf import settings


register = template.Library()

@register.simple_tag
def site_base():
	return settings.APP_BASE

@register.simple_tag
def static_base():
	return settings.STATIC_BASE

@register.simple_tag
def ext_base():
	return settings.EXT_BASE

# @register.simple_tag
# def allow_anon_buyers():
#     return settings.ALLOW_ANON_BUYERS
