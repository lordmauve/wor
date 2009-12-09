function get_ajax_object()
{
	// Get an AJAX object appropriate for the browser we're running in.
	if(window.ActiveXObject)
	{
		return new ActiveXObject("Msxml2.XMLHTTP"); //newer versions of IE5+
		//return new XDomainRequest() //IE8+ only. A more "secure", versatile alternative to IE7's XMLHttpRequest() object.
	}
	else if(window.XMLHttpRequest)
		//IE7, Firefox, Safari etc
		return new XMLHttpRequest();
	else
		return false;
}

function get_json(url, callback, postdata)
{
	var req = get_ajax_object();

	req.onreadystatechange = function () {
		if (req.readyState == 4) {
			if (req.status == 200) {
				if (typeof JSON !== 'undefined') {
					var arg = JSON.parse(req.responseText);
				} else {
					var arg = eval('(' + req.responseText + ')');
				}
				//firebug doesn't catch errors in XHR events?
				//so queue event on a short timer
				setTimeout(function () {callback(arg);}, 10) 
			} else {
				handle_api_error(req);
			}
		}
	};

	if (postdata) {
		req.open("POST", url, true);
		req.send(postdata);
	} else {
		req.open("GET", url, true);
		req.send();
	}
}

var EditorPane = {
	timeofday: '',
	TIMES_OF_DAY: ['', 'sunset', 'night', 'sunrise'],

	proto: null,
	proto_icons: {},


	init: function () {
		var map_layer = $('map-layer');
		new DragAndDrop.Controller($('map'), map_layer);
		var mo = /(-?\d+),(-?\d+)/.exec(location.hash)
		if (mo) {
			var x = parseInt(mo[1], 10);
			var y = parseInt(mo[2], 10);
			map_layer.setStyle({
				left: (map_layer.offsetLeft - x) + 'px',
				top: (map_layer.offsetTop - y) + 'px',
			});
		}

		var map = $('map');
		var pos = map.cumulativeOffset();
		map.setStyle({
			height: (document.viewport.getHeight() - pos.top - 26) + 'px',
			borderBottom: 'none'
		});
		
		EditorPane.setupToolbar();
	
		$$('#map .emptyloc a').each(function (a) {
			Event.observe(a, 'click', EditorPane.newLocation);
		});

		EditorPane.showProtoPanel();

		$('protopanel').setStyle({
			height: (document.viewport.getHeight() - pos.top - 36) + 'px',
			borderBottom: 'none'
		});

		$('panel').observe('load', EditorPane.showIframe);
	},

	showProtoPanel: function () {
		//show a panel of prototype tiles
		$('panel').hide();

		if (!$('protopanel')) {
			var protopanel = new Element('div', {id: 'protopanel'});
			$('map').insert({before: protopanel});
			get_json('/editor/location-types', EditorPane.populateProtoPanel);
		} else {
			$('protopanel').show();
		}
	},

	showIframe: function () {
		$('protopanel').hide();
		$('panel').show();
	},

	populateProtoPanel: function (types) {
		var protopanel = $('protopanel');
		$A(types).each(function (t) {
			protopanel.insert(new Element('h3').update(t[0]));
			$A(t[1]).each(function (ts) {
				var key = ts[0];
				var name = ts[1];
				var im = new Element('img', {src: '/tiles/' + name.toLowerCase() + '.png', title: name});
				im.key = ts[0];
				protopanel.insert(im);
				Event.observe(im, 'click', EditorPane.selectProto.bind(im));
				EditorPane.proto_icons[key] = im;
			});
		});
	},

	selectProto: function () {
		if (EditorPane.proto) {
			EditorPane.proto_icons[EditorPane.proto].removeClassName('selected');
		}
		this.addClassName('selected');
		EditorPane.proto = this.key;
	},

	setupToolbar: function () {
		EditorPane.addToolbarButton('Edit another region', function () { location.href = '/editor/';});
		EditorPane.addToolbarButton('Toggle time of day', EditorPane.nextTimeOfDay);
		EditorPane.addToolbarButton('Toggle names', function () { $('map').toggleClassName('hidenames');});
	},

	addToolbarButton: function (label, callback) {
		var button = new Element('button').update(label);
		$('toolbar').insert(button);
		button.observe('click', callback);
	},

	nextTimeOfDay: function () {
		var i = EditorPane.TIMES_OF_DAY.indexOf(EditorPane.timeofday);
		var nexttime = EditorPane.TIMES_OF_DAY[(i + 1) % EditorPane.TIMES_OF_DAY.length];
		document.body.id = nexttime;
		EditorPane.timeofday = nexttime;
		var p = (nexttime) ? nexttime + '/' : '';
		$('map').select('.loc').each(function (loc) {
			var mo = /loc (.*)/.exec(loc.className);
			var u = "url('/tiles/" + p + mo[1].toLowerCase() + ".png')";
			loc.style.backgroundImage = u;
		});
	},

	newLocation: function (event) {
		var target = Event.element(event);
		if (target.nodeName != 'a')
			target = target.up('a');
		Event.stop(event);

		if (EditorPane.proto) {
			get_json(target.pathname + 'json', EditorPane.updateMap, 'type=' + escape(EditorPane.proto));
		}
	},

	updateMap: function(newtiles) {
		var tile = new Element('div', {'class': 'loc'});

		var tod = EditorPane.timeofday;
		var tilepath = (tod) ? tod + '/' : '';

		$A(newtiles).each(function (t) {
			var sx = t[0];
			var sy = t[1];
			var sz = t[2];
			var wx = t[3][0];
			var wy = t[3][1];
			if (t[4]) {
				var tile = new Element('div', {
							'id': 'tile-' + wx + '-' + wy,
							'class': 'loc ' + t[5]
						});
				tile.update('<a href="' + location.pathname + wx + ',' + wy + '/" target="panel">' + t[4] + '</a>');
				tile.setStyle({
					left: sx + 'px',
					top: sy + 'px',
					zIndex: sz,
					backgroundImage: "url('/tiles/" + tilepath + t[5].toLowerCase() + ".png')"
				});
				if ($(tile.id))
					$(tile.id).remove();
				$('map-layer').appendChild(tile);
			} else {
				var tile = new Element('div', {
							'id': 'tile-' + wx + '-' + wy,
							'class': 'emptyloc'
						});
				tile.update('<a href="' + location.pathname + 'new/' + wx + ',' + wy + '/" target="panel"><img src="/icons/add.png" alt="+"></a>');
				tile.setStyle({
					left: sx + 'px',
					top: sy + 'px',
					zIndex: sz
				});
				if ($(tile.id))
					$(tile.id).remove();
				$('map-layer').appendChild(tile);
				Event.observe(tile.select('a')[0], 'click', EditorPane.newLocation);
			}	
		});
	}
};

Event.observe(window, 'load', EditorPane.init);
