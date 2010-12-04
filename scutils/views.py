# Create your views here.
from django.conf import settings

def set_vars(request):
    """
    Returns custom context variables required by this app from settings.py
    """
    try:
        allow_anon_users = settings.ALLOW_ANON_USERS
    except AttributeError:
        allow_anon_users = False
    context_extras = {}
    context_extras['REQ_PATH'] = request.path
    context_extras['REQ_FULL_PATH'] = request.get_full_path()
    context_extras['ALLOW_ANON_USERS'] = allow_anon_users
    return context_extras


"""
A request processor that returns dictionary to be merged into a
template context. Function takes the request object as its only
parameter
and returns a dictionary to add to the context.

These are referenced from the setting TEMPLATE_CONTEXT_PROCESSORS and
used by DjangoContext.
"""

import time, hashlib, struct

def gen_sec_link(uri_prefix, secret, rel_path):
    """returns url for lighttpd mod_secure_download
        eg /sdl/<token>/<hashtimestamp>/my_secure_doc.pdf
    """
    hextime = "%08x" % time.time()
    # NB rel_path must start with a slash
    if not rel_path.startswith('/'):
        rel_path = '/%s' % rel_path
    token = hashlib.md5(secret + rel_path + hextime).hexdigest()
    return '%s%s/%s%s' % (uri_prefix, token, hextime, rel_path)

def check_sec_link(secret, token, hextime, rel_path):
    """The time seems to be shortened by hex, so can't compare hextime with today
        This will return true if the token matches the secret+hextime+rel_path
        and the hextime is within the last 24 hours"""
    if not rel_path.startswith('/'):
        rel_path = '/%s' % rel_path
    token_ok = (token == hashlib.md5(secret + rel_path + hextime).hexdigest())
    in_time = False
    if token_ok:
        hexnow = "%08x" % time.time()
        secs = struct.unpack('!f', hextime.decode('hex'))[0]
        secsnow = struct.unpack('!f', hexnow.decode('hex'))[0]
        then = time.gmtime(secs)
        now = time.gmtime(secsnow)
        diff =  time.gmtime(secsnow - secs)
        # these are secs from epoch - 1970, 1, 1, ...
        # this will check diff is less than 24 hrs
        in_time = diff[0] == 1970 and diff[1] == 1 and diff[2] < 3
    return token_ok, in_time
    
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist

"""
Modified from http://www.djangosnippets.org/snippets/1451/ by DHoy
"""

def mini_render_to_response(template, try_mobile = False, *args, **kwargs):
    render = None
    if try_mobile:
        try:
            file, ext = template.split('.')
        except ValueError: pass
        else:
            mini_template = file + '_mini.' + ext
            try:
                render = render_to_response(mini_template, *args, **kwargs)
            except TemplateDoesNotExist: pass
    
    if not render:
        render = render_to_response(template, *args, **kwargs)
    
    return render

