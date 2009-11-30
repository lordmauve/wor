from django import forms

from wor.db import db
from wor.accounts import AuthenticationFailure

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

