from django.conf import settings
from django.contrib.auth.decorators import login_required


def login_required_or_allow_anon_user(function=None, redirect_field_name=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    if settings.ALLOW_ANON_USERS:
        return function
        
    return login_required(function, redirect_field_name)
    # actual_decorator = user_passes_test(
    #     lambda u: u.is_authenticated(),
    #     redirect_field_name=redirect_field_name
    # )
    # if function:
    #     return actual_decorator(function)
    # return actual_decorator
