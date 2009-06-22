////////////
// Messages

function update_messages()
{
	basic_ajax_get("/actor/self/log", load_messages);
}

function load_messages(req)
{
	if(req.readyState == 4)
	{
		var panel = get_side_panel("messages");
		if(req.status == 200)
		{
			panel.innerHTML = "";
			// Parse the input stream, and construct the panel
			var messages = parse_input_table(req.responseText, 3);
			for(var i in messages)
			{
				var bits = messages[i];
				var when = new Date();
				when.setTime(bits[0] * 1000);

				panel.innerHTML += "<div class='message msg_type_" + bits[1] + "'>"
								 + "<span class='timestamp'>"
								 + format_date_time(when)
								 + "</span> "
								 + bits[2]
								 + "</div>";
			}
		}
		else
		{
			panel.innerHTML = "Error loading messages.\n<div>" + req.responseText + "</div>";
		}
	}
}
