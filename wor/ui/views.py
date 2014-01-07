from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie

from wor.db import db

from forms import *
from recaptcha import verify_recaptcha


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            if verify_recaptcha(request):
                # create account
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                realname = form.cleaned_data['real_name']
                email = form.cleaned_data['email']

                account = db.accounts().create_account(
                    username=username,
                    password=password,
                    realname=realname,
                    email=email
                )

                # create player within account
                player_name = form.cleaned_data['player_name']
                alignment = form.cleaned_data['alignment']

                account.create_player(player_name, alignment)
                db.commit()

                request.session['account'] = account.username
                return HttpResponseRedirect('/game')
            else:
                form._errors['__all__'] = form.error_class([u"Captcha failed."])
    else:
        form = RegistrationForm()
    return render_to_response('register.html', {'form': form, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['user']
            request.session['account'] = account.username
            return HttpResponseRedirect('/game')
    else:
        form = LoginForm()

    return render_to_response('login.html', {'form': form})


@ensure_csrf_cookie
def game(request):
    if 'account' not in request.session:
        return HttpResponseRedirect('/')
    account = db.accounts().get_account(request.session['account'])
    player = account.get_players()[0]
    return render_to_response('game.html', {'actor': player, 'account': account})
