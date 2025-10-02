from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.models import User
def social_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # require at least one connected social account
        if not request.user.socialaccount_set.exists():
            # send them to the page where they can connect
            return redirect('socialaccount_connections')
        return view_func(request, *args, **kwargs)
    return _wrapped

