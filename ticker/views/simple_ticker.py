import json

from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

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
        token = PresentationToken.objects.filter(
            token=request.session['token'],
            field_id=args[0],
            is_used=False
        ).first()
        if token is None:
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
    fa = FieldAllocation.objects.filter(field_id=field_id, is_active=True).first()
    game = fa.game if fa else None
    field = fa.field if fa else None
    return render(request, 'user/simple_ticker_interface.html', dict(game=game, field=field))


@has_valid_token
def api_simple_ticker(request, field_id, response_type):
    response_type = None if response_type == '/' or response_type == '' else response_type
    token = request.session['token']
    token = PresentationToken.objects.get(token=token)
    fa = FieldAllocation.objects.get(is_active=True, field=token.field)
    field = fa.field
    game = fa.game
    match = game.get_match()

    if str(field.id) != field_id:
        messages.error(request, 'Invalid field id for this token')
        return HttpResponseRedirect(reverse_lazy('ticker_interface_simple', args=[field.id]))

    if match is None:
        messages.error(request, 'Match does not exist')
        return HttpResponseRedirect(reverse_lazy('ticker_interface_simple', args=[field.id]))

    updated_information = dict()
    set = game.get_current_set()
    if 'team_a' in request.POST:
        if request.POST['team_a'] == '+':
            set.add_point_team_a(match.rule)
        elif request.POST['team_a'] == '-':
            set.remove_point_team_a(match.rule)
        updated_information['type'] = 'score-update'
        updated_information['game_id'] = game.id
        updated_information['set_id'] = set.id
        updated_information['field_id'] = field.id
        updated_information['set_number'] = set.set_number
        updated_information['set_score'] = set.get_score()
        updated_information['game_score'] = game.get_sets()
        updated_information['set_finished'] = set.is_finished(match.rule)
    elif 'team_b' in request.POST:
        if request.POST['team_b'] == '+':
            set.add_point_team_b(match.rule)
        elif request.POST['team_b'] == '-':
            set.remove_point_team_b(match.rule)
        updated_information['type'] = 'score-update'
        updated_information['game_id'] = game.id
        updated_information['set_id'] = set.id
        updated_information['field_id'] = field.id
        updated_information['set_number'] = set.set_number
        updated_information['set_score'] = set.get_score()
        updated_information['game_score'] = game.get_sets()
        updated_information['set_finished'] = set.is_finished(match.rule)
    elif 'switch_set' in request.POST:
        if game.is_won(match.rule):
            messages.info(request, 'Game is won. Removed it from the field')
            fa = FieldAllocation.objects.filter(game=game, field__id=field.id, is_active=True)
            fa.update(
                is_active=False,
                end_allocation=timezone.now()
            )
            updated_information['type'] = 'clear-field'
            updated_information['field_id'] = field.id
            updated_information['game_field_link'] = reverse_lazy('remove_game_to_field', args=[game.id, field.id])
            updated_information['game_name'] = game.name
            updated_information['game_id'] = game.id
        elif game.get_current_set().is_finished(match.rule):
            game.current_set += 1
            game.save()

            set = game.get_current_set()
            updated_information['type'] = 'update-current-set'
            updated_information['field_id'] = field.id
            updated_information['set_number'] = game.current_set
            updated_information['set_label'] = 'Satz {0}'.format(set.set_number)
            updated_information['set_score'] = set.get_score()
        else:
            updated_information = dict(error='Cannot switch sets at this stage')
    if response_type is not None:
        return HttpResponse(json.dumps(updated_information))
    return HttpResponseRedirect(reverse_lazy('ticker_interface_simple', args=[field.id]))
