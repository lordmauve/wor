// Map-drawing functions

var Map = {
	locations: [],

	update: function () {
		get_json("/location/neighbourhood", Map.load_neighbourhood);
	},

	load_neighbourhood: function (raw_locations) {
		var locations = Array();
		LocationBubble.close();

		// Initialise the centre hex (FIXME: assumes that at least
		// one hex was returned)
		locations[0] = Array(raw_locations[0]);

		var ring = 1;
		var ring_pos = 0;
		for(var i = 1; i < raw_locations.length; i++)
		{
			// Create a new ring if we need to
			if(locations.length < ring+1)
			{
				locations[ring] = Array();
			}

			// Put this hex in its place
			locations[ring][ring_pos] = raw_locations[i];

			// Move the coordinates round to the next hex
			ring_pos += 1;
			if(ring_pos >= ring * 6)
			{
				ring_pos = 0;
				ring += 1;
			}
		}

		// Now, for each hex in the grid, go round and set its
		// properties
		var newlocations = [];
		for(var r = 0; r < locations.length; r++)
		{
			for(var d = 0; d < locations[r].length; d++) {
				var loc = locations[r][d];
				var xy = Map.rd_to_xy(r, d);
				var x = xy[0];
				var y = xy[1];
				newlocations.push(Map.set_location(x, y, loc))
			}
		}

		// delete additional locations
		for (var i = newlocations.length; i < Map.locations.length; i++) {
			if (Map.locations[i])
				Map.locations[i].remove();
		}
		Map.locations = newlocations;
                LocationBubble.show($('map0-0'));
	},

	TILE_WIDTH: 117,
	TILE_HEIGHT: 73,

	ORIGIN_X: 300,
	ORIGIN_Y: 400,

	screen_pos: function (wx, wy) {
		var sx = parseInt((wx + 0.5 * wy) * Map.TILE_WIDTH + 0.5);
		var sy = -parseInt((wy * 0.5 * Math.pow(3, 0.5)) * Map.TILE_HEIGHT + 0.5);
		var z = 10000 - wy;

		sx += Map.ORIGIN_X;
		sy += Map.ORIGIN_Y;
		return {x: sx, y: sy, z: z};
	},

	set_time_of_day: function (tod) {
		if (tod == 'daytime')
			document.body.id = '';
		else
			document.body.id = tod;
	},

	set_location: function (x, y, loc) {
		// sets the location at (x, y), returning the corresponding HTML Element
		// or null if the location was empty
		var cellid = "map" + x + "-" + y;
		if (x == 0 && y == 0 && loc.timeofday)
			Map.set_time_of_day(loc.timeofday);

		var tile = $(cellid);
		if (!loc || loc == 'unknown') {
			if (tile) {
				tile.remove();
			}
			return null;
		}
		if (tile == null)
		{
			var tile = new Element('div', {'class': 'loc', id: cellid});
			var screen = Map.screen_pos(x, y)
			tile.setStyle({
				left: screen.x + 'px',
				top: screen.y + 'px',
				zIndex: screen.z
			});
			$('map').insert(tile);
			
			Event.observe(tile, 'click', Map.show_bubble.bindAsEventListener(tile)); 
		}
		else {
			tile.select('.tile').each(function (x) {x.remove();});
		}

		var tilesrc = loc.class_name.toLowerCase() + '.png';
		if (document.body.id)
			tilesrc = document.body.id + '/' + tilesrc;
		tilesrc = '/tiles/' + tilesrc;
		
		var im = new Element('img', {'src': tilesrc, 'class': 'tile'});
		tile.appendChild(im);

		Map.update_actors(tile, loc.actors);

		tile.loc = loc;

		return $(cellid);
	},

	update_actors: function (tile, actors) {
		tile.select('img.actor').each(function (x) {x.remove();});
	
		if (actors.length == 1) {
			Map.insert_actor(tile, 0, 0, actors[0]);
		} else if (actors.length < 8) {
			var ang = (3.141592 * 2) / actors.length;
			actors.each(function (a, i) {
				var x = 40 * Math.sin(ang * i);
				var y = 22 * Math.cos(ang * i);

				Map.insert_actor(tile, x, y, a);
			});
		}
	},

	available_npcs: ['Barmaid'],

	insert_actor: function(tile, x, y, a) {
		var img = new Element('img', {'class': 'actor'});
		if (a.id == Player.player.id) {
			img.src = '/img/pc/me-' + a.alignment.toLowerCase() + '.png';
			var xoff = -15;
			var name = a.name;
		} else if (a.alignment) {
			img.src = '/img/pc/' + a.alignment.toLowerCase() + '.png';
			var xoff = -7;
			var name = a.name;
		} else if (a.class_name) {
			parts = a.class_name.split('.')
			var p = parts.pop();
			img.src = '/img/npc/' + p.toLowerCase() + '.png';
			var xoff = -7;
			var name = a.short_name;
		}
		img.alt = name;
		img.title = name;
		img.setStyle({
			left: (x + 53 + xoff) + 'px',
			bottom: (y + 45) + 'px',
			zIndex: (y + 45)
		});
		tile.insert(img);
	},


	// Convert [r, d] "polar" coordinates to an internal (x, y) pair
	rd_to_xy: function (r, d) {
		if(r == 0)
			return Array(0, 0);

		var sector = Math.floor(d / r);
		var direction = 1;
		if(sector >= 3)
		{
			sector -= 3;
			direction = -1;
		}
		var distance = d % r;

		var x = -9999;
		var y = -9999;

		switch(sector)
		{
			case 0:
				x = direction * (r - distance);
				y = direction * distance;
				break;
			case 1:
				x = direction * -distance;
				y = direction * r;
				break;
			case 2:
				x = direction * -r;
				y = direction * (r - distance);
				break;
		}

		return Array(x, y);
	},

	// Convert internal cartesian (x, y) coordinates to an [r, d] pair.
	xy_to_rd: function (x, y)
	{
		if(x == 0 && y == 0)
			return Array(0, 0);

		var r = Math.max(Math.abs(x), Math.max(Math.abs(y), Math.abs(x+y)));

		// Handle the six sectors separately
		// 0° to 60°
		if(x > 0 && y >= 0)
			d = y;
		// 60° to 120°
		else if(y > 0 && (x == 0 || -x < y))
			d = r - x;
		// 120° to 180°
		else if(y > 0)
			d = 3*r - y;
		// 180° to 240°
		else if(x < 0 && y <= 0)
			d = 3*r - y;
		// 240° to 300°
		else if(y < 0 && (x == 0 || x < -y))
			d = 4*r + x;
		// 300° to 360°
		else
			d = 6*r + y;

		return Array(r, d);
	},

	show_bubble: function (event) {
		// if the event came from the tile and not the
		// bubble, update
		var el = event.element();
		
		//TODO: show the bubble for this actor icon clicked on?
		if (el.up('div').hasClassName('loc'))
			LocationBubble.show(this);
	},
};

var LocationBubble = {
	bubble: null,	

	show: function (tile) {
		LocationBubble.close();
		LocationBubble.create();
		tile.appendChild(LocationBubble.bubble);
		LocationBubble.update(tile.loc);
	},

	update: function (loc) {
		var bubble = LocationBubble.bubble;
		bubble.select('h3')[0].update(loc.title);

		$('scrollpane').update('');

		if (loc.description) {
			$('scrollpane').insert(new Element('p', {'class': 'description'}).update(loc.description));
		}

		var npcs = loc.actors.filter(function (a) {return !!a.class_name;});

		if (npcs.length) {
			var npcslist = new Element('div', {'class': 'playersection'});
		
			var section_title = npcs.length + ' other character' + ((npcs.length != 1) ? 's' : '');
			var section_summary = npcs[0].short_name.substr(0, 1).toUpperCase() + npcs[0].short_name.substr(1);
			if (npcs.length == 2)
				section_summary += ' and ' + npcs[1].short_name;
			else if (npcs.length > 2) {
				var n_others = (npcs.length - 2);
				section_summary +=  ', ' + npcs[1].short_name + ' and ' + n_others + (n_others == 1) ? 'other.' : 'others.';
			}
	
			var player_tree = new CollapsibleTree(npcslist, section_title, section_summary);
			for (var i = 0; i < npcs.length; i++) {
				var a = npcs[i];
				var act_tree = new CollapsibleTree(player_tree, a.full_name, '');

				$A(a.actions).each(function (act) {
					new Action(act, act_tree);
				});
			}
	
			$('scrollpane').insert(npcslist);
		}

		//other actors only
		var actors = loc.actors.filter(function (a) {return !a.class_name && a.id != Player.player.id;});

		if (actors.length) {
			var other_players = new Element('div', {'class': 'playersection'});
		
			var section_title = actors.length + ' other player' + ((actors.length != 1) ? 's' : '');
			var section_summary = actors[0].name;
			if (actors.length == 2)
				section_summary = actors[0].name + ' and ' + actors[1].name;
			else if (actors.length > 2) {
				var n_others = (actors.length - 2);
				section_summary = actors[0].name + ', ' + actors[1].name + ' and ' + n_others + (n_others == 1) ? 'other.' : 'others.';
			}
	
			var player_tree = new CollapsibleTree(other_players, section_title, section_summary);
			for (var i = 0; i < actors.length; i++) {
				var a = actors[i];

				var ptitle = '<img src="/icons/icon-' + a.alignment.toLowerCase() + '.png" class="alignicon" /> ' + a.name;
				var act_tree = new CollapsibleTree(player_tree, ptitle, '');

				$A(a.actions).each(function (act) {
					new Action(act, act_tree);
				});
			}
	
			$('scrollpane').insert(other_players);
		}


		if (loc.objects.length) {
			for (var i = 0; i < loc.objects.length; i++) {
				var o = loc.objects[i];
				var objectsection = new Element('div', {'class': 'objectsection'});
				var obj_tree = new CollapsibleTree(objectsection, o.name);
				if (o.description) {
					o.description.split('\n\n').each(function (para) {
						var p = new Element('p', {'class': 'description'});
						p.appendChild(document.createTextNode(para));
						obj_tree.insert(p);
					});
				}
				$A(o.actions).each(function (act) {
					new Action(act, obj_tree);
				});
				$('scrollpane').insert(objectsection);
			}
		}

	},
	
	create: function () {
		var bubble = new Element('div', {id: 'map-bubble'});
		bubble.insert(new Element('h3'));

		var scrollpane = new Element('div', {'id': 'scrollpane'});
		bubble.insert(scrollpane);

		var tail = new Element('img', {'src': '/img/bubble-tail.png', id: 'bubble-tail'});
		bubble.insert(tail);

		var close = new Element('img', {'src': '/icons/close.png', id: 'bubble-close'});
		bubble.insert(close);
		Event.observe(close, 'click', LocationBubble.close);

		LocationBubble.bubble = bubble;
	},

	close: function () {
		if (LocationBubble.bubble)
			LocationBubble.bubble.remove();
		LocationBubble.bubble = null;
	}
}

// An expandable/collapsible tree widget
var CollapsibleTree = Class.create({
	initialize: function(parent, title, summary) {
		this.container = new Element('div', {'class': 'collapsible collapsible-empty'});
		this.titlebox = new Element('div', {'class': 'head'});
		this.panel = new Element('div', {'class': 'contents'});

		this.titlebox.insert(new Element('h3').update(title));
		this.summary = new Element('span').update(summary);
		this.titlebox.insert(this.summary);

		this.container.insert(this.titlebox);
		this.container.insert(this.panel);
		this.panel.hide();

		parent.insert(this.container);

		this.titlebox.observe('click', this.toggle.bindAsEventListener(this));
	},

	insert: function (obj) {
		this.panel.insert(obj);	
		if (this.container.hasClassName('collapsible-empty'))
			this.container.removeClassName('collapsible-empty');
	},
	
	toggle: function (event) {
		this.summary.toggle();
		this.panel.toggle();
		if (this.panel.visible()) {
			this.container.addClassName('collapsible-open');
		}
		else this.container.removeClassName('collapsible-open');
	}
});
