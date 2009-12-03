from django import forms

from wor.world.location import Location


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
