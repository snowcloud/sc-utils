from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def login_required_or_allow_anon_user(function=None, redirect_field_name=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    if settings.ALLOW_ANON_USERS:
        return function
    
    # TODO: THIS BREAKS IF USER NOT LOGGED IN- RETURNS REDIRECT?
    # FIXED: was happening cause used to wrap function called in view,
    # ok if used on view itself
    # could probably use this:
    # return login_required(function, redirect_field_name)
    # or the code from login_required is...
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
