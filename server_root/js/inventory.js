// Inventory handling

// Start to select an item from the player's inventory
function show_items()
{
	var select_panel = document.getElementById("inventory_panel");
	select_panel.innerHTML = "<table id='inventory_panel_table'></table>";
	select_panel.style.visibility = 'visible';

	var account = document.getElementById("account").value
	var password = document.getElementById("password").value
	var actid = document.getElementById("actorid").value

	var req = get_ajax_object();
	req.onreadystatechange = function() { inventory_response(req); }
	req.open("GET", api + "/actor/self/inventory", true, account, password);
	req.setRequestHeader("X-WoR-Actor", actid);

	req.send("");
}

function inventory_response(req)
{
	if(req.readyState == 4)
	{
		var select_table = document.getElementById("inventory_panel_table");
		if(req.status == 200)
		{
			// Get the table of item data
			var items = parse_input_table(req.responseText, 4);
			items.sort(function(a,b) {
						if(a[3] == b[3]) return 0;
						if(a[3] < b[3]) return -1;
						return 1;
					});

			nlines = Math.floor((items.length-1)/3) + 1;
			for(var i=0; i<nlines; i++)
			{
				var line = "<tr>";
				for(var j=0; j<3; j++)
				{
					line += "<td>";
					pos = j*nlines + i;
					if(pos < items.length)
					{
						line += "<a href='javascript:inventory_change(";
						line += items[pos][1];
						line += ")'>" + items[pos][3];
						if(items[pos][2] > 1)
							line += " (x" + items[pos][2] + ")";
						line += "</a>";
					}
					line += "</td>";
				}
				line += "</tr>";
				select_table.innerHTML += line;
			}
		}
		else
		{
			// FIXME: Report an error
		}
	}
}

function inventory_change(item_id)
{
	var data = new Array();
	data[inventory_parameters] = item_id;
	post_action_data(inventory_action, data);
	var select_panel = document.getElementById("inventory_panel");
	select_panel.style.visibility = 'hidden';
}
