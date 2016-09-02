from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ticker.models import FieldAllocation
from ticker.models import PresentationToken


def has_valid_token(f):
    def wrap(request, *args, **kwargs):
        # this check the session if userid key exist, if not it will redirect to login page
        if 'token' not in request.session.keys():
            return HttpResponseRedirect(reverse('ticker_interface_login'))

        token_valid = PresentationToken.is_valid(request.session['token'])
        if not token_valid:
            return HttpResponseRedirect(reverse('ticker_interface_login'))

        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap

def simple_ticker_login(request):
    if request.user.is_authenticated():
        messages.info(request, 'Sie sind bereits eingeloggt')
    return render(request, 'user/simple_ticker_authenticate.html', dict())


@has_valid_token
def simple_ticker_interface(request, field_id):
    fa = FieldAllocation.objects.filter(field_id=field_id).first()
    game = fa.game if fa else None
    return render(request, 'user/simple_ticker_interface.html', dict(game=game))


@has_valid_token
def api_simple_ticker(request):

    return HttpResponse('OK')