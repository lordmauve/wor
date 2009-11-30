from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response

from wor.db import db
from wor.world.location import NullLocation, Location
from Position import Position

from forms import *


def regions(request):
	regions = db.world().regions.items()
	return render_to_response('editor/regions.html', {'regions': regions})


def screen_pos(wx, wy):
	tw = 117
	th = 73
	sx = int((wx + 0.5 * wy) * tw + 0.5)
	sy = -int((wy * 0.5 * 3 ** 0.5) * th + 0.5)
	z = 10000 - wy
	return sx, sy, z
	

def edit_region(request, region_id):
	try:
		region = db.world().get_region(region_id)
	except KeyError:
		raise Http404()

	locations = {}
	for coord, loc in region.locations.items():
		sx, sy, z = screen_pos(*coord)
		locations[coord] = (sx, sy, z, loc)
		for dx, dy in [(1, 0), (-1, 0), (0, 1), (-1, 1), (1, -1), (0, -1)]:
			x, y = dx + coord[0], dy + coord[1]
			if (x, y) in locations:
				continue
			try:
				adj = region[x, y]
			except KeyError:
				sx, sy, z = screen_pos(x, y)
				locations[x, y] = (sx, sy, z, None)

	locations = [k + v for k, v in locations.items()]
	
	return render_to_response('editor/map.html', {'region': region, 'region_id': region_id, 'locations': locations})


def edit_location(request, region_id, x, y):
	from Position import Position
	location = db.world()[Position(int(x), int(y), region_id)]

	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			location.title = form.cleaned_data['title']
			location.description = form.cleaned_data['description']
			# TODO: commit message
			db.commit()
			return HttpResponseRedirect('/editor/%s/' % region_id)
	else:
		form = LocationForm(initial={
			'title': location.title,
			'description': location.description,
		})

	return render_to_response('editor/location.html', {'location': location, 'form': form})


def new_location(request, region_id, x, y):
	region = db.world().get_region(region_id)
	coords = int(x), int(y)

	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			l = Location(
				title=form.cleaned_data['title'],
				description=form.cleaned_data['description']
			)
			region.set_location(coords, l)
			# TODO: commit message
			db.commit()
			return HttpResponseRedirect('/editor/%s/' % region_id)
	else:
		form = LocationForm()

	return render_to_response('editor/location.html', {'form': form})
