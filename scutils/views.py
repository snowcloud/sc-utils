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

# import time, hashlib, struct
from datetime import date
import hashlib

def gen_sec_link(uri_prefix, secret, rel_path, day=None):
    """returns url for lighttpd mod_secure_download
        eg /sdl/<token>/<hashtimestamp>/my_secure_doc.pdf
    """
    day = day or date.today().strftime('%Y-%m-%d')
    # NB rel_path must start with a slash
    if not rel_path.startswith('/'):
        rel_path = '/%s' % rel_path
    token = hashlib.md5(secret + rel_path + day).hexdigest()
    return '%s%s/%s%s' % (uri_prefix, token, day, rel_path)

def check_sec_link(secret, token, daystr, rel_path):
    """
        This will return true if the token matches the secret+daystr+rel_path
        and the daystr (YYYY-MM-DD) is within the last 24 hours"""
    if not rel_path.startswith('/'):
        rel_path = '/%s' % rel_path
    token_ok = (token == hashlib.md5(secret + rel_path + daystr).hexdigest())
    in_time = False
    if token_ok:
        try:
            t1,t2,t3 = daystr.split('-')
            day = date(int(t1),int(t2),int(t3))
            timedelta = date.today() - day
            in_time = timedelta.days >= 0 and timedelta.days <= 1
        except:
            pass
    return token_ok, in_time

# def gen_sec_link(uri_prefix, secret, rel_path):
#     """returns url for lighttpd mod_secure_download
#         eg /sdl/<token>/<hashtimestamp>/my_secure_doc.pdf
#     """
#     hextime = "%08x" % time.time()
#     # NB rel_path must start with a slash
#     if not rel_path.startswith('/'):
#         rel_path = '/%s' % rel_path
#     token = hashlib.md5(secret + rel_path + hextime).hexdigest()
#     return '%s%s/%s%s' % (uri_prefix, token, hextime, rel_path)

# def check_sec_link(secret, token, hextime, rel_path):
#     """The time seems to be shortened by hex, so can't compare hextime with today
#         This will return true if the token matches the secret+hextime+rel_path
#         and the hextime is within the last 24 hours"""
#     if not rel_path.startswith('/'):
#         rel_path = '/%s' % rel_path
#     token_ok = (token == hashlib.md5(secret + rel_path + hextime).hexdigest())
#     in_time = False
#     if token_ok:
#         hexnow = "%08x" % time.time()
#         secs = struct.unpack('!f', hextime.decode('hex'))[0]
#         secsnow = struct.unpack('!f', hexnow.decode('hex'))[0]
#         then = time.gmtime(secs)
#         now = time.gmtime(secsnow)
#         diff =  time.gmtime(secsnow - secs)
#         # these are secs from epoch - 1970, 1, 1, ...
#         # this will check diff is less than 24 hrs
#         in_time = diff[0] == 1970 and diff[1] == 1 and diff[2] < 3
#     return token_ok, in_time
    
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

"""
View which can render and send email from a contact form.
Modified from contact_form.views.py
Needs to:
    - only respond to POST
    - read success_url from the form data
    - read error_url from the form data
Form does vlaidation
"""

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from scutils.forms import SimpleStaticSiteContactForm

@csrf_exempt
def external_contact_form(request, form_class=SimpleStaticSiteContactForm,
                 extra_context=None,
                 fail_silently=False):
    """
    Render a contact form, validate its input and send an email
    from it.

    **Optional arguments:**

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``fail_silently``
        If ``True``, errors when sending the email will be silently
        supressed (i.e., with no logging or reporting of any such
        errors. Default value is ``False``.

    ``form_class``
        The form to use. If not supplied, this will default to
        ``contact_form.forms.ContactForm``. If supplied, the form
        class must implement a method named ``save()`` which sends the
        email from the form; the form class must accept an
        ``HttpRequest`` as the keyword argument ``request`` to its
        constructor, and it must implement a method named ``save()``
        which sends the email and which accepts the keyword argument
        ``fail_silently``.

    **Context:**

    ``form``
        The form instance.
    """
    fail_url = None
    if request.method == 'POST':
        fail_url = request.POST.get('fail_url', None)
        form = form_class(data=request.POST, files=request.FILES, request=request)
        if form.is_valid():
            form.save(fail_silently=fail_silently)
            return HttpResponseRedirect(form.cleaned_data['success_url'])
        else:
            if fail_url:
                return HttpResponseRedirect(fail_url)
    
    raise Http404

    # return HttpResponse("Hello, world.")

