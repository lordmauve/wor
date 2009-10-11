/////////////
// Map-drawing functions

function update_map()
{
	basic_ajax_get("/location/neighbourhood", load_neighbourhood);
}

function load_neighbourhood(req)
{
	if(req.readyState == 4)
	{
		if(req.status == 200)
		{
			var raw_locations = parse_input(req.responseText);
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
					body = document.getElementById("map_b" + r + "_" + d);
					if(body == null)
						continue;
					if(loc.name == null)
						loc.name = "";

					body.innerHTML = loc.name;
					var image_name = "/img/terrain/render-T-";
					image_name += loc.stack;
					image_name += "-B1--B2-";
					image_name += ".png";
					body.style.backgroundImage = "url(\"" + image_name + "\")";
				}
			}
		}
		else
		{
			for(var r = 0; r < 3; r++)
			{
				for(var d = 0; d < r*6; d++)
				{
					body = document.getElementById("map_b" + r + "_" + d);
					if(body == null)
						continue;
					body.innerHTML = "";
				}
			}
		}
	}
}
