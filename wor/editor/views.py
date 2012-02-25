from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response

from wor.jsonutil import JSONResponse
from wor.db import db
from wor.world.location import NullLocation, Location
from Position import Position

from forms import *

from django.template import RequestContext


def template(request, template, **kwargs):
    """Helper method for calling render_to_response with a RequestContext"""
    return render_to_response(template, kwargs, context_instance=RequestContext(request))


def regions(request):
    regions = db.world().regions.items()
    return render_to_response('editor/regions.html', {'regions': regions})


def screen_pos(wx, wy):
    # spaced out
    tw = 117
    th = 73
    # packed tight
#    tw = 100
#    th = 64
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
            if form.cleaned_data['type'] != location.internal_name():
                ltype = Location.get_class(form.cleaned_data['type'])
                desc = form.cleaned_data['description']
                if not desc:
                    desc = None
                
                l = ltype(
                    title=form.cleaned_data['title'],
                    description=desc
                )
                #TODO: copy any other data
                location.region.set_location((int(x), int(y)), l)
            else:
                location.title = form.cleaned_data['title']
                desc = form.cleaned_data['description']
                if desc:
                    location.description = desc
                else:
                    try:
                        del location.description
                    except AttributeError:
                        pass
            # TODO: commit message
            db.commit()
            sx, sy, sz = screen_pos(location.pos.x, location.pos.y)
            return HttpResponseRedirect('/editor/%s/' % region_id + '#%d,%d' % (sx, sy))
    else:
        initial = {
            'title': location.title,
            'description': location.description,
            'type': location.internal_name(),
        }
        if location.description == location.__class__.description:
            del initial['description']
        form = LocationForm(initial=initial)

    return render_to_response('editor/location.html', {'location': location, 'form': form})


def new_location(request, region_id, x, y):
    region = db.world().get_region(region_id)
    coords = int(x), int(y)

    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            ltype = Location.get_class(form.cleaned_data['type'])
            l = ltype(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description']
            )
            region.set_location(coords, l)
            # TODO: commit message
            db.commit()
            sx, sy, sz = screen_pos(*coords)
            return HttpResponseRedirect('/editor/%s/' % region_id + '#%d,%d' % (sx, sy))
    else:
        form = LocationForm()

    return render_to_response('editor/location.html', {'form': form})


def create_region(request):
    if request.method == 'POST':
        form = CreateRegionForm(request.POST)
        if form.is_valid():
            internal_name = form.cleaned_data['internal_name']
            title = form.cleaned_data['title']

            w = db.world()
            region = w.create_region(internal_name, title)
            db.commit()

            return HttpResponseRedirect('/editor/%s/' % internal_name)
    else:
        form = CreateRegionForm()

    return template(request, 'editor/create-region.html', form=form)


def location_types(request):
    return JSONResponse(get_location_type_choices())


def new_location_json(request, region_id, x, y):
    region = db.world().get_region(region_id)
    coords = int(x), int(y)

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    form = LocationForm(request.POST)
    if form.is_valid():
        ltype = Location.get_class(form.cleaned_data['type'])
        loc = ltype()
        region.set_location(coords, loc)
        db.commit()
        sx, sy, sz = screen_pos(*coords)

        locations = [(sx, sy, sz, coords, loc.get_title(), loc.class_name())]
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (-1, 1), (1, -1), (0, -1)]:
            x, y = dx + coords[0], dy + coords[1]
            try:
                adj = region[x, y]
            except KeyError:
                sx, sy, z = screen_pos(x, y)
                locations.append((sx, sy, z, (x, y), None))
        return JSONResponse(locations)
    return JSONResponse(form._errors)
