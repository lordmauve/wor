from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from forms import *

from wor.db import db

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


def game(request):
	account = db.accounts().get_account(request.session['account'])
	player = account.get_players()[0]
	return render_to_response('game.html', {'actor': player, 'account': account})
