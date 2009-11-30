////////////
// Base player state

// Global to hold the details of the player, for use by other functions
var player;

function update_player_details()
{
	get_json("/actor/self/desc", load_basic_player);
}

function load_basic_player(player)
{
	// Set up the first panel: Basic player info
	var top_panel = document.getElementById("top_panel");
	// Success! Create a Player
	// Despatch the request for the currently-held item ASAP
	//update_held_item(player.holding);

	panel = "<table><tr>";
	panel += "<td class='header'><b>" + player.name + "</b></td>";
	panel += "<td class='header'>AP " + player.ap + "/" + player.ap_counter.maximum + "</td>";
	panel += "<td class='header'>HP " + player.hp + "/" + player.maxhp + "</td>";
	panel += "</tr></table>";

	top_panel.innerHTML = panel;

	// Error here: Server didn't return 200
	//top_panel.innerHTML = "Error loading player details.\n<div>" + req.responseText + "</div>";
}

////////////
// Actions

function update_player_actions()
{
	get_json("/actor/self/actions", load_player_act);
}

var inventory_action = "";
var inventory_parameter = "";

function load_player_act(actions)
{
	var actions_panel = get_side_panel("player_actions");
	var inventory_found = false;

	var fragments = [];

	for (var i=0; i < actions.length; i++)
	{
		var act = actions[i];

		if(act.group == 'inventory')
		{
			action_id = act.uid.split('.');
			if (action_id[2] == 'changeitem')
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
			fragments.push(act.html);
		}
		else
		{
			fragments.push(act.html);
		}
	}
	if(inventory_found)
	{
		fragments.push("<button onclick='show_items()'>Change item</button>");
	}

	actions_panel.innerHTML = fragments.join('<hr>');
}

////////////////////
// Action handling
function post_action()
{
	var fuid = arguments[0];
	var data = {};

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
	data['action'] = fuid;
	get_json('/actor/self/actions/', act_response, $H(data).toQueryString());
}

function act_response(resp)
{
	// Go through the response one line at a time, and update
	// what we're told to (one update per line)

	// FIXME: Or, for now, just trigger a full set of updates
	update_player_details();
	update_player_actions();
	MessagePane.update();
	update_map();
}
