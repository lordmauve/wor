//////////////
// Held item

var held_item;

function update_held_item(itemid)
{
	if(itemid)
	{
		basic_ajax_get("/item/" + itemid + "/desc", load_held_item);
	}
	else
	{
		// FIXME: Clean up (or remove) the Item panel
	}
}

function load_held_item(req)
{
	if(req.readyState == 4)
	{
		var item_panel = get_item_panel();
		if(req.status == 200)
		{
			var its = parse_input(req.responseText);
			held_item = its[0];

			var header = document.getElementById("held_item_header");
			var body = document.getElementById("held_item_body");

			if(held_item.name)
				header.innerHTML = held_item.name;
			else
				header.innerHTML = held_item.type;

			if(held_item.description)
				body.innerHTML = held_item.description;
			else
				body.innerHTML = "";
		}
	}
}

function get_item_panel()
{
	var item_panel = get_side_panel("held_item");

	if(item_panel.innerHTML == "")
	{
		item_panel.innerHTML = "<h2 id='held_item_header'></h2>\n";
		item_panel.innerHTML += "<div id='held_item_body'></div>\n";
		item_panel.innerHTML += "<div id='held_item_actions'></div>\n";
	}

	return item_panel;
}
