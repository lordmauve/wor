////////////
// Messages

var MessagePane = {
	update: function () {
		get_json("/actor/self/log", MessagePane.show_messages);
	},

	show_messages: function (messages) {
		var panel = get_side_panel("messages");

		var html = ''
		var alignments = ['wood', 'earth', 'water', 'fire', 'metal'];
		for (var i = 0; i < messages.length; i++)
		{
			var bits = messages[i];
			var when = new Date(bits[0] * 1000);
			var alignment = (bits[4]) ? alignments[bits[4]] : null;

			html += MessagePane.format_message(when, bits[1], bits[2], bits[3], alignment);
		}
		panel.innerHTML = html;
	},
	
	format_message: function (when, type, message, sender, alignment) {
		if (MessagePane['format_message_' + type])
			return MessagePane['format_message_' + type](when, message, sender, alignment);
		return MessagePane.format_message_default(when, type, message);
	},

	formatted_name: function (sender, alignment) {
		return '<span class="' + alignment + '">' + sender + '</span>';
	},

	format_message_say: function (when, message, sender, alignment) {
		return '<div class="message say">' + MessagePane.formatted_name(sender, alignment) + ' says<br>' +
			'&emsp;' + message + '</div>';
	},

	format_message_action: function (when, message, sender, alignment) {
		return '<div class="message action">' + MessagePane.formatted_name(sender, alignment) + ' ' + message + '</div>';
	},

	format_message_default: function (when, type, message) {
		return '<div class="message msg_type_' + type + '">'
			 + '<span class="timestamp" title="' + when.toLocaleString() + '">'
			 + when.toLocaleTimeString()
			 + "</span> "
			 + message
			 + "</div>";
	}
};
