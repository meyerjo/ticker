from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import CharField
from django.db.models import Value
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.timezone import now

from ticker.forms.matchplan import MatchForm, GameLineUpForm, GameLineUpFormSet
from ticker.forms.presentation import PresentationForm, SlideForm
from ticker.models import Club, Team, Player, Season, League
from ticker.models import ColorDefinition
from ticker.models import DefinableColor
from ticker.models import FieldAllocation
from ticker.models import Game
from ticker.models import Match
from ticker.models import Profile
from ticker.models.presentation import Presentation, Slide, PresentationSlideTeam


@login_required
def manage_clubs(request):
    clubs = Club.objects.all().order_by('club_name')
    return render(request, 'user/manage_clubs.html', dict(clubs=clubs))


@login_required
def manage_club_details(request, clubid):
    clubs = Club.objects.all().order_by('club_name')
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_clubs.html', dict(clubs=clubs, details=club))


@login_required
def manage_team_details(request, teamid):
    teams = Team.objects.filter(id=int(teamid)).first()
    clubs = Club.objects.all()
    return render(request, 'user/manage_teams.html', dict(team=teams,
                                                          possible_sex=Player.possible_sex,
                                                          clubs=clubs))


@login_required
def manage_players_club(request, clubid):
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_players_club.html', dict(club=club))


@login_required
def manage_fields(request, clubid):
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_fields.html', dict(club=club))


@login_required
def manage_season(request, season_id=None):
    season = Season.objects.get(id=season_id) if season_id is not None else None
    context = dict(seasons=Season.get_seasons(), season=season)
    return render(request, 'user/manage_season.html', context)


@login_required
def manage_league(request, league_id=None):
    if league_id is not None:
        league = League.objects.get(id=league_id)
    else:
        league = None
    context = dict(leagues=League.objects.all(),
                   teams=Team.objects.all(),
                   seasons=Season.objects.filter(active=True),
                   league=league
                   )
    return render(request, 'user/manage_league.html', context)


@login_required
def manage_dashboard(request):
    p = Profile.objects.filter(user=request.user).first()
    club = p.associated_club if p is not None else None

    matches = Match.objects.filter(canceled=False, match_time__range=[now()-timedelta(days=2), now()+timedelta(days=2)])
    if club is not None:
        matches = matches.filter(team_a__parent_club=club) | matches.filter(team_b__parent_club=club)
    context = dict(matches=matches)
    return render(request, 'user/manage_dashboard.html', context)


@login_required
def manage_ticker_interface(request, match_id):
    match = Match.objects.get(id=match_id)

    ModelFormSet = modelformset_factory(Game, form=GameLineUpForm, formset=GameLineUpFormSet)
    formset = ModelFormSet(queryset=match.get_all_games())

    if request.POST:
        if 'unlock_field' not in request.POST and match.has_lineup():
            messages.error(request, 'Feld muss entsichert werden')
        else:
            formset = ModelFormSet(request.POST)
            if not formset.is_valid():
                messages.error(request, 'Formset is not valid')
                try:
                    formset.clean()
                except BaseException as e:
                    messages.error(request, str(e))
            else:
                formset.save(True)
                messages.success(request, 'Selection valid')

    context = dict(match=match, formset=formset)
    return render(request, 'user/tickerinterface.html', context)


@login_required
def manage_ticker(request):
    if request.user.is_superuser:
        matches = Match.all_matches()
    else:
        p = Profile.objects.filter(user=request.user).first()
        if p is None:
            matches = []
        else:
            matches = Match.objects.filter(team_a__parent_club=p.associated_club) | \
                      Match.objects.filter(team_b__parent_club=p.associated_club)
    return render(request, 'user/manage_ticker.html', dict(matches=matches))


@login_required
def manage_colors(request):
    possible_definitions = DefinableColor.objects.all().annotate(color=Value(None, CharField())).values('id', 'name', 'color')
    p = Profile.objects.filter(user=request.user).first()
    if p is not None:
        cd = ColorDefinition.objects.filter(club=p.associated_club)
        for color_definition in cd:
            for i, elm in enumerate(possible_definitions):
                if possible_definitions[i]['name'] == color_definition.color_definition.name:
                    possible_definitions[i]['color'] = color_definition.color_hexcode
                    continue
        colors = possible_definitions
    else:
        colors = None
    return render(request, 'user/manage_colors.html', dict(colors=colors))


def login(request):
    from django.contrib.auth import authenticate, login
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('manage_dashboard'))

    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'user/login.html', dict())
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('manage_dashboard'))
    else:
        messages.error(request, 'Login didnot match')
        return render(request, 'user/login.html', dict())


@login_required
def manage_game(request, game_id):
    game = Game.objects.filter(id=game_id).first()
    if game is not None:
        return render(request, 'user/manage_game.html', dict(game=game))
    messages.error(request, 'Game does not exist')
    return HttpResponseRedirect(reverse_lazy('manage_ticker'))


@login_required()
def manage_edit_player_profile(request, player_id):
    player = Player.objects.filter(id=player_id).first()
    return render(request, 'user/manage_player_profile.html', dict(player=player))


@login_required()
def manage_edit_matchdate(request, matchdate_id):
    match = Match.objects.filter(id=matchdate_id).first()
    form = MatchForm(instance=match)

    if request.POST:
        form = MatchForm(request.POST, instance=match)
        if form.is_valid() and form.has_changed():
            with transaction.atomic():
                form.save()
                messages.success(request, 'Success')
        else:
            messages.error(request, 'Form is not valid')

    return render(request, 'user/manage_edit_matchdate.html', dict(form=form))


@login_required()
def manage_presentation(request, presentation=None):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    p = Profile.objects.filter(user=request.user).first()
    club = p.associated_club

    presentations = Presentation.objects.filter(team__parent_club=club)
    if presentation is not None:
        selected_presentation = presentations.filter(id=presentation).first()
        slides = Slide.objects.filter(presentationslideteam__presentation=selected_presentation)
    else:
        slides = None

    return render(request, 'user/manage_presentations.html', dict(presentations=presentations, slides=slides))


@login_required()
def manage_presentation_new(request):
    p = Profile.objects.filter(user=request.user).first()
    club = p.associated_club
    presentation_form = PresentationForm(prefix='presentation')
    SlideFormSet = formset_factory(SlideForm)
    slides = SlideFormSet(prefix='slides')

    if request.POST:
        print(request.POST)
        presentation_form = PresentationForm(request.POST, prefix='presentation')
        slides = SlideFormSet(request.POST, prefix='slides')
        if presentation_form.is_valid():
            if slides.is_valid():

                with transaction.atomic():
                    presentation = presentation_form.instance
                    presentation.save()

                    team = presentation.team

                    for slide in slides:
                        s = slide.instance
                        print(s.__dict__)
                        print(s.club_id)
                        s.club_id = club.id
                        s.save()

                        pst = PresentationSlideTeam.objects.create(presentation=presentation, slide=s, slide_number=1)
            else:
                messages.error(request, 'Slides are not valid')
        else:
            messages.error(request, 'PresentationForm is not valid')
        return HttpResponseRedirect(reverse('manage_load_presentation', presentation.id))

    return render(request, 'user/manage_new_presentation.html', dict(presentation_form=presentation_form,
                                                                      slide_formset=slides))

