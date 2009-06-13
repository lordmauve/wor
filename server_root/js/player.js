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
// Actions
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
			if(panel.innerHTML != "")
				panel.innerHTML += "<hr/>"
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

////////////////////
// Action handling
function post_action()
{
	var fuid = arguments[0];
	var account = document.getElementById("account").value
	var password = document.getElementById("password").value
	var actid = document.getElementById("actorid").value

	// Perform a simple action (i.e. with no parameters, just a button)
	var act_req = get_ajax_object();
	act_req.onreadystatechange = function() { act_response(act_req); };
	act_req.open("POST", api + "/actor/self/actions", true, account, password);
	act_req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
	act_req.setRequestHeader("X-WoR-Actor", actid)

	return_data = "action:" + fuid + "\r\n";
	for(var i in arguments)
	{
		if(i == 0) { continue; }
		data = arguments[i];
		elt = document.getElementById(data);
		if(elt)
		{
			return_data += data + ":" + elt.value + "\r\n";
		}
	}
	act_req.setRequestHeader("Content-Length", return_data.length)

	act_req.send(return_data);
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
			update_messages();
		}
		else
		{
			// FIXME: Add feedback if the action failed.
		}
	}
}
