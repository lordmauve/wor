////////////
// Base player state
function load_basic_player(req)
{
	if(req.readyState == 4)
	{
		// Set up the first panel: Basic player info
		var top_panel = document.getElementById("top_panel");
		if(req.status == 200)
		{
			// Success! Create a Player
			var ps = parse_input(req.responseText);
			var p = ps[0];
			
			panel = "<table><tr>";
			panel += "<td class='header'><b>" + p['name'] + "</b></td>";
			panel += "<td class='header'>AP " + p['ap.value'] + "/" + p['ap.maximum'] + "</td>";
			panel += "<td class='header'>HP " + p['hp'] + "/" + p.maxhp + "</td>";
			panel += "</tr></table>";

			top_panel.innerHTML = panel;
		}
		else
		{
			// Error here: Server didn't return 200
			top_panel.innerHTML = "Error loading player details.\n<div>" + req.responseText + "</div>";
		}
	}
}

////////////
// Player-specific actions
function load_player_act(req)
{
  if(req.readyState == 4)
  {
    var panel = get_side_panel("player_actions");

    if(req.status == 200)
    {
      // Get the array of action objects
	  actions = parse_input(req.responseText);
      panel.innerHTML = "";
      for(var aid in actions)
      {
		  act = actions[aid];
		  panel.innerHTML += act['html'];
      }
    }
    else
    {
      // Error here: No 200 response
      panel.innerHTML = "Error loading actions.\n<div>" + req.responseText + "</div>";
    }
  }
}

// Parse a standard key/value input stream, and return an array of the
// objects read

function parse_input(str)
{
	var result = new Array();
	var accumulator = new Object();

    var lines = str.split("\n");
    for(var n in lines)
    {
		var line = lines[n];
		var kv = new Array();
		if(line[0] == ' ')
		{
			accumulator[kv[0]] += "\n" + line;
		}
		else if(line == '-')
		{
			result.push(accumulator);
			accumulator = new Object();
			hasdata = false;
		}
		else if(line == '')
		{ }
		else
		{
			kv = line.split(":", 2);
			accumulator[kv[0]] = kv[1];
			hasdata = true;
		}
    }

    if(hasdata)
	{
		result.push(accumulator);
	}
	return result;
}

////////////////////
// Action handling
function act_simple(fuid)
{
	// Perform a simple action (i.e. with no parameters, just a button)
	var act_req = get_ajax_object();
	act_req.onreadystatechange = function() { act_response(act_req); };
	act_req.open("POST", api + "/actor/self/action", true, "darksatanic", "wor");
	act_req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
	act_req.setRequestHeader("X-WoR-Actor", "1")
	act_req.send("action="+fuid);
}

// FIXME: Add an act_complex which takes a list of form fields and
// returns those fields' data to the server in the .send() call

function act_response(req)
{
	if(req.readyState == 4)
	{
		if(req.status == 200)
		{
			// Go through the response one line at a time, and update
			// what we're told to (one update per line)

			// FIXME: Or, for now, just trigger a full set of updates
			update_player_details();
			update_player_actions();
		}
		else
		{
			// FIXME: Add feedback if the action failed.
		}
	}
}
