// Map-drawing functions
var DISPLAY_RANGE = 2;

var Map = {
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
		for(var r = 0; r < locations.length; r++)
		{
			for(var d = 0; d < locations[r].length; d++) {
				var loc = locations[r][d];
				var xy = Map.rd_to_xy(r, d);
				var x = xy[0];
				var y = xy[1];
				Map.set_location(x, y, loc)
			}
		}
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

	set_location: function (x, y, loc) {
		var cellid = "map" + x + "-" + y;

		var tile = $(cellid);
		if (!loc) {
			if (tile) {
				tile.remove();
			}
			return;
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

		tile.setStyle({
			backgroundImage: "url('/tiles/" + loc.class_name.toLowerCase() + ".png')"
		});

		tile.loc = loc;
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
		if (event.element().hasClassName('loc'))
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

		if (loc.actors.length) {
			var other_players = new Element('div', {'class': 'playersection'});
		
			var section_title = loc.actors.length + ' other players';
			var section_summary = loc.actors[0].name;
			if (loc.actors.length == 2)
				section_summary = loc.actors[0].name + ' and ' + loc.actors[1].name;
			else if (loc.actors.length > 2) {
				var n_others = (loc.actors.length - 2);
				section_summary = loc.actors[0].name + ', ' + loc.actors[1].name + ' and ' + n_others + (n_others == 1) ? 'other.' : 'others.';
			}
	
			var player_tree = new CollapsibleTree(other_players, section_title, section_summary);
			for (var i = 0; i < loc.actors.length; i++) {
				var a = loc.actors[i];
				var p = new Element('p');
				p.update('<img src="/icons/icon-' + a.alignment.toLowerCase() + '.png" class="alignicon" /> ' + a.name + '');
				player_tree.insert(p);
			}
	
			$('scrollpane').insert(other_players);
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
		this.container = new Element('div', {'class': 'collapsible'});
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
	},
	
	toggle: function (event) {
		this.summary.toggle();
		this.panel.toggle();
//		if (this.panel.visible()) {
//			this.container.addClassName('collapsible-open');
//		}
//		else this.container.removeClassName('collapsible-open');
	}
});
