###
# Copyright (c) 2006-2007, Jared Kuolt
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the SuperJared.com nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
###

from django.conf import settings
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect

import re

class RequireLoginMiddleware(object):
    """
    Require Login middleware. If enabled, each Django-powered page will
    require authentication.
    
    If an anonymous user requests a page, he/she is redirected to the login
    page set by REQUIRE_LOGIN_PATH or /accounts/login/ by default.
    """
    def __init__(self):
        self.require_login_path = getattr(settings, 'REQUIRE_LOGIN_PATH', '/accounts/login/')
    
    def process_request(self, request):
        if getattr(settings, 'DISABLE_REQUIRE_LOGIN', False):
            return None
        if not self.allowed_path(request.path) and request.user.is_anonymous():
            if request.POST:
                return login(request)
            else:
                return HttpResponseRedirect('%s?next=%s' % (self.require_login_path, request.path))
    
    def allowed_path(self, requested_path):
        for p in settings.AUTH_ALLOWED_PATHS:
            if re.search(p, requested_path):
                return True
        return requested_path == self.require_login_path

class AdminRedirectMiddleware:
    """ allows you to customize redirects with the GET line in the admin """

    def process_response(self, request, response):
        # save redirects if given
        
        # mod JDH - if no trailing slash, request is WSGIRequest and has no attr session
        try:
            if request.method == "GET" and request.GET.get("next", False):
                request.session["next"] = request.GET.get("next")

        # apply redirects
            if request.session.get("next", False) and \
            type(response) == HttpResponseRedirect and \
            request.path.startswith("/admin/"):
                path = request.session.get("next")
                del request.session["next"]
                return HttpResponseRedirect(path)
        except AttributeError:
            pass
        return response


from django.http import HttpResponseForbidden
from django.template import RequestContext, loader

def forbidden(request, template_name='403.html'):
    """Default 403 handler"""

    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))

class Custom403Middleware(object):
      """Catches 403 responses and renders 403.html"""

      def process_response(self, request, response):

          if isinstance(response, HttpResponseForbidden):
             return forbidden(request)
          else:
             return response

import threading

_thread_locals = threading.local()

def get_current_user():
    try:
        return _thread_locals.user
    except AttributeError:
        return None

class ThreadLocals(object):
	"""Middleware that adds various objects to thread local storage from the request object."""
	def process_request(self, request):
		_thread_locals.user = getattr(request, 'user', None)

