/////////////
// Map-drawing functions

// FIXME: Move this initialisation of the logging infrastructure to
// another file.

// Create the logger
var log = log4javascript.getLogger(); 

// Create a PopUpAppender with default options
var popUpAppender = new log4javascript.PopUpAppender();

// Change the desired configuration options
popUpAppender.setFocusPopUp(true);
popUpAppender.setNewestMessageAtTop(true);

// Add the appender to the logger
log.addAppender(popUpAppender);

// Disable all logging
// FIXME: Make this dependent on a player stat
log4javascript.setEnabled(false);

var DISPLAY_RANGE = 2;

function update_map()
{
	get_json("/location/neighbourhood", load_neighbourhood);
}

function load_neighbourhood(raw_locations)
{
	var locations = Array();

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
		for(var d = 0; d < locations[r].length; d++)
		{
			loc = locations[r][d];
			var xy = rd_to_xy(r, d);
			var x = xy[0];
			var y = xy[1];

			log.debug("Setting location xy = (" + x + ", " + y + "), rd = [" + r + ", " + d + "]")

			var body = document.getElementById("map_b" + x + "_" + y);
			if(body == null)
			{
				log.debug("Skipping non-present hex: map_b" + x + "_" + y);
				continue;
			}
			if(loc.name == null)
				loc.name = "";

			var rd = xy_to_rd(x, y);

			body.innerHTML = loc.name;

			// Set the hex body image
			var locstack = loc.stack;

			if(locstack == null)
				locstack = "";

			var image_name = "/img/terrain/default/body";
			image_name += "-T-" + loc.stack;
			image_name += ".png";
			body.style.backgroundImage = "url(\"" + image_name + "\")";

			// Set the images above the body
			if(y >= 0)
			{
				var elt_name = "map_e" + x + "_" + y + "_n";
				var edge = document.getElementById(elt_name + "w");
				if(edge == null)
					log.debug("Skipping missing edge: " + elt_name + "w");
				else
				{
					var rd = xy_to_rd(x-1, y+1);
					var nbrstack = "";
					if(rd[0] <= DISPLAY_RANGE)
					{
						var nbr = locations[rd[0]][rd[1]];
						nbrstack = nbr.stack;
					}
					if(nbrstack == null)
						nbrstack = "";

					var image_name = "/img/terrain/default/edge-D-F";
					image_name += "-T1-" + nbrstack;
					image_name += "-T2-" + locstack;
					image_name += ".png";
					edge.style.backgroundImage = "url(\"" + image_name + "\")";
					//edge.innerHTML = "(" + (x-1) + ", " + (y+1) + ")<br/>(" + x + ", " + y + ")";
					//edge.innerHTML = nbrstack + "<br/>" + locstack;
				}

				edge = document.getElementById(elt_name + "e");
				if(edge == null)
					log.debug("Skipping missing edge: " + elt_name + "e");
				else
				{
					var rd = xy_to_rd(x, y+1);
					var nbrstack = "";
					if(rd[0] <= DISPLAY_RANGE)
					{
						var nbr = locations[rd[0]][rd[1]];
						nbrstack = nbr.stack;
					}
					if(nbrstack == null)
						nbrstack = "";

					var image_name = "/img/terrain/default/edge-D-R";
					image_name += "-T1-" + nbrstack;
					image_name += "-T2-" + locstack;
					image_name += ".png";
					edge.style.backgroundImage = "url(\"" + image_name + "\")";
					//edge.innerHTML = "(" + x + ", " + (y+1) + ")<br/>(" + x + ", " + y + ")";
					//edge.innerHTML = nbrstack + "<br/>" + locstack;
				}
			}

			// Set the images below the body
			if(y <= 0)
			{
				var elt_name = "map_e" + x + "_" + y + "_s";
				var edge = document.getElementById(elt_name + "w");
				if(edge == null)
					log.debug("Skipping missing edge: " + elt_name + "w");
				else
				{
					var rd = xy_to_rd(x, y-1);
					var nbrstack = "";
					if(rd[0] <= DISPLAY_RANGE)
					{
						var nbr = locations[rd[0]][rd[1]];
						nbrstack = nbr.stack;
					}
					if(nbrstack == null)
						nbrstack = "";

					var image_name = "/img/terrain/default/edge-D-R";
					image_name += "-T1-" + locstack;
					image_name += "-T2-" + nbrstack;
					image_name += ".png";
					edge.style.backgroundImage = "url(\"" + image_name + "\")";
					//edge.innerHTML = "(" + x + ", " + y + ")<br/>(" + x + ", " + (y-1) + ")";
					//edge.innerHTML = locstack + "<br/>" + nbrstack;
				}

				edge = document.getElementById(elt_name + "e");
				if(edge == null)
					log.debug("Skipping missing edge: " + elt_name + "e");
				else
				{
					var rd = xy_to_rd(x+1, y-1);
					var nbrstack = "";
					if(rd[0] <= DISPLAY_RANGE)
					{
						var nbr = locations[rd[0]][rd[1]];
						nbrstack = nbr.stack;
					}
					if(nbrstack == null)
						nbrstack = "";

					var image_name = "/img/terrain/default/edge-D-F";
					image_name += "-T1-" + locstack;
					image_name += "-T2-" + nbrstack;
					image_name += ".png";
					edge.style.backgroundImage = "url(\"" + image_name + "\")";
					//edge.innerHTML = "(" + x + ", " + y + ")<br/>(" + (x+1) + ", " + (y-1) + ")";
					//edge.innerHTML = locstack + "<br/>" + nbrstack;
				}
			}
		}
	}
}

// Convert [r, d] "polar" coordinates to an internal (x, y) pair
function rd_to_xy(r, d)
{
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
}

// Convert internal cartesian (x, y) coordinates to an [r, d] pair.
function xy_to_rd(x, y)
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
}
