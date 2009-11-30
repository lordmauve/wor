// Inventory handling

// Start to select an item from the player's inventory
function show_items()
{
	var req = get_json("/actor/self/inventory", inventory_response);
}

function inventory_response(items)
{
	var select_panel = document.getElementById("inventory_panel");
/*	items.sort(function(a,b) {
				if(a[3] == b[3]) return 0;
				if(a[3] < b[3]) return -1;
				return 1;
			});*/

	var txt = '';

	for (var i = 0; i < items.length; i++){
		var item = items[i];
		txt += "<a href='javascript:inventory_change(";
		txt += item.id;
		txt += ")'>" + item.name;
		txt += "</a> ";
	}
	
	select_panel.innerHTML = txt;
	select_panel.style.visibility = 'visible';
}

function inventory_change(item_id)
{
	var data = new Array();
	data[inventory_parameters] = item_id;
	post_action_data(inventory_action, data);
	var select_panel = document.getElementById("inventory_panel");
	select_panel.style.visibility = 'hidden';
}
