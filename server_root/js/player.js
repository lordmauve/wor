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
	var panel = get_side_panel('player');
	
	var html = "<h3>" + player.name + "</h3>";

	html += "<p><span>" + player.ap_counter.value + "/" + player.ap_counter.maximum + " AP</span>";
	html += "<span>" + player.hp + "/" + player.maxhp + ' <img src="/img/hp.png" alt="HP"></span></p>';

	panel.update(html);
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
			fragments.push(act);
		}
		else
		{
			new Action(act);
		}
	}
	if(inventory_found)
	{
		fragments.push("<button onclick='show_items()'>Change item</button>");
	}
}

var Action = Class.create({
	initialize: function (act) {
		this.act = act;
		var label = act.caption;
		if (act.cost)
			label += ' (' + act.cost + ')';

		var button = document.createElement('button', {'class': 'action'}).update(label);
		var actions_panel = get_side_panel("player_actions");
		actions_panel.insert(button);

		Event.observe(button, 'click', this.perform.bindAsEventListener(this));
	},
	
	perform: function () {
		post_action(this.act.uid);
	}
});


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
