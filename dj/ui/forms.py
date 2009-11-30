from django import forms

from wor.db import db
from wor.accounts import AuthenticationFailure

from Alignment import Alignment


# FIXME: make Alignment properly enumerate the choices
ALIGNMENT_CHOICES = [(a, Alignment(a).name()) for a in range(5)]


class RegistrationForm(forms.Form):
	username = forms.RegexField(regex=r'^\w+$', min_length=5, max_length=64, error_messages={'invalid': u"Your username may only consist of upper- and lowercase letters, numbers and underscores"})

	password = forms.CharField(min_length=5, max_length=64, widget=forms.PasswordInput)
	password_confirm = forms.CharField(
		widget=forms.PasswordInput,
		label="Password (Again)",
		help_text=u"Please re-enter your chosen password to confirm.",
	)

	real_name = forms.CharField(label='Your real name', max_length=128)
	email = forms.EmailField(label='E-mail', max_length=128, help_text=u"This is for administrator use only and will not be made public.")
	
	player_name = forms.RegexField(regex=r'^[A-Za-z \'-]+', max_length=32, error_messages={'invalid': u"Your character name may only contain latin letters, spaces, apostrophes and hyphens"})
	alignment = forms.ChoiceField(choices=ALIGNMENT_CHOICES)

	def clean_username(self):
		"""Validate that the username is not taken."""
		value = self.cleaned_data['username']
		if db.accounts().is_username_taken(value):
			raise forms.ValidationError(u"This username is already taken.")
		return value.strip()

	def clean_player_name(self):
		"""Validate that the player name is not taken."""
		value = self.cleaned_data['player_name']
		if db.world().is_player_name_taken(value):
			raise forms.ValidationError(u"This player name is already taken. Please choose again.")
		return value.strip()

	def clean(self):	
		values = self.cleaned_data
		password = values.get('password', None)
		password_confirm = values.get('password_confirm', None)
		if password and password_confirm and password != password_confirm:
			raise forms.ValidationError("The passwords supplied do not match.")
		return values


class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		"""Check that the username and password is a valid login;
		if so, self.cleaned_data will contain a key 'user' that is the account logged into"""

		username = self.cleaned_data.get('username', None)
		password = self.cleaned_data.get('password', None)
	
		if username and password:
			try:
				account = db.accounts().authenticate(username, password)
			except AuthenticationFailure:
				raise forms.ValidationError(u"The username and password you have entered were not correct.")
			else:
				return {'user': account}

