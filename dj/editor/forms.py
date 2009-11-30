from django import forms

class LocationForm(forms.Form):
	title = forms.CharField()
	description = forms.CharField(required=False, widget=forms.Textarea)
