////////////
// Base player state

// Global to hold the details of the player, for use by other functions
var player;

function update_player_details()
{
	basic_ajax_get("/actor/self/desc", load_basic_player);
}

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
			player = ps[0];
			
			// Despatch the request for the currently-held item ASAP
			update_held_item(player.holding);

			panel = "<table><tr>";
			panel += "<td class='header'><b>" + player.name + "</b></td>";
			panel += "<td class='header'>AP " + player['ap.value'] + "/" + player['ap.maximum'] + "</td>";
			panel += "<td class='header'>HP " + player.hp + "/" + player.maxhp + "</td>";
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

function update_player_actions()
{
	basic_ajax_get("/actor/self/actions", load_player_act);
}

var inventory_action = "";
var inventory_parameter = "";

function load_player_act(req)
{
	if(req.readyState == 4)
	{
		var actions_panel = get_side_panel("player_actions");

		if(req.status == 200)
		{
			// Get the array of action objects
			actions = parse_input(req.responseText);
			actions_panel.innerHTML = "";
			var inventory_found = false;
			for(var aid in actions)
			{
				act = actions[aid];

				if(act.group == 'inventory')
				{
					action_id = act.uid.split('.');
					if(action_id[2] == 'changeitem')
					{
						// Keep track of the details, but don't display
						// anything
						inventory_action = act.uid;
						pos = act.parameters.indexOf('_');
						inventory_parameters = act.parameters.slice(pos+1);
						inventory_found = true;
					}
				}
				else if(act.group == 'item')
				{
					var panel = get_item_panel();
					var actions = document.getElementById("held_item_actions");
					if(actions.innerHTML != "")
						actions.innerHTML += "<hr/>";
					actions.innerHTML += act.html;
				}
				else
				{
					if(actions_panel.innerHTML != "")
						actions_panel.innerHTML += "<hr/>";
					actions_panel.innerHTML += act.html;
				}
			}
			if(inventory_found)
			{
				if(actions_panel.innerHTML != "")
					actions_panel.innerHTML += "<hr/>";
				actions_panel.innerHTML += "<button onclick='show_items()'>Change item</button>";
			}
		}
		else
		{
			// Error here: No 200 response
			actions_panel.innerHTML = "Error loading actions.\n<div>" + req.responseText + "</div>";
		}
	}
}

////////////////////
// Action handling
function post_action()
{
	var fuid = arguments[0];
	var data = new Array();

	// Extract the requested data from the 
	for(var i=1; i<arguments.length; i++)
	{
		param_name = arguments[i];
		elt = document.getElementById(param_name);
		if(elt)
		{
			split_point = data.indexOf('_');
			key = param_name.slice(split_point+1);
			data[key] = elt.value;
		}
	}

	post_action_data(fuid, data);
}

function post_action_data(fuid, data)
{
	var account = document.getElementById("account").value
	var password = document.getElementById("password").value
	var actid = document.getElementById("actorid").value

	// Perform a simple action (i.e. with no parameters, just a button)
	var act_req = get_ajax_object();
	act_req.onreadystatechange = function() { act_response(act_req); };
	act_req.open("POST", api + "/actor/self/actions", true, account, password);
	act_req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	act_req.setRequestHeader("X-WoR-Actor", actid);

	return_data = "action:" + fuid + "\r\n";
	for(var key in data)
	{
		return_data += key + ":" + data[key] + "\r\n";
	}
	act_req.setRequestHeader("Content-Length", return_data.length)

	act_req.send(return_data);
}

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
