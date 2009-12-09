from django import forms

from wor.world.location import Location
from wor.db import db


def get_location_type_choices():
	choices = {}
	for k, v in Location.list_all_classes().items():
		mod, name = k.rsplit('.', 1)
		choices.setdefault(mod, []).append((k, v.__name__))
	return choices.items()


class LocationForm(forms.Form):
	type = forms.ChoiceField(choices=get_location_type_choices())

	title = forms.CharField(required=False)
	description = forms.CharField(required=False, widget=forms.Textarea)


class CreateRegionForm(forms.Form):
	internal_name = forms.RegexField(regex=r'^[\w.-]+$')
	title = forms.CharField(required=False)

	def clean_internal_name(self):
		value = self.cleaned_data['internal_name'].strip()
		world = db.world()
		if value in world.regions:
			raise forms.ValidationError("This internal name is already in use for another region.")
		return value
