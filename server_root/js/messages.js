////////////
// Messages

var MessagePane = {
	update: function () {
		get_json("/actor/self/log", MessagePane.show_messages);
	},

	show_messages: function (messages) {
		var panel = get_side_panel("messages");

		var html = ''
		for (var i = 0; i < messages.length; i++)
		{
			var bits = messages[i];
			var when = new Date(bits[0] * 1000);

			html += '<div class="message msg_type_' + bits[1] + '">'
							 + '<span class="timestamp" title="' + when.toLocaleString() + '">'
							 + when.toLocaleTimeString()
							 + "</span> "
							 + bits[2]
							 + "</div>";
		}
		panel.innerHTML = html;
		// panel.innerHTML = "Error loading messages.\n<div>" + req.responseText + "</div>";
	}
};
