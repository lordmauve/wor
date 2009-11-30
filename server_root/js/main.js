////////////
// Main function: Called to initiate loading the page contents

var api = "http://" + document.domain + "/api";

function load_game()
{
	update_player_details();
	update_player_actions();
	update_map();
	update_messages();
}

////////////
// Library functions

function get_ajax_object()
{
	// Get an AJAX object appropriate for the browser we're running in.
	if(window.ActiveXObject)
	{
		return new ActiveXObject("Msxml2.XMLHTTP"); //newer versions of IE5+
		//return new XDomainRequest() //IE8+ only. A more "secure", versatile alternative to IE7's XMLHttpRequest() object.
	}
	else if(window.XMLHttpRequest)
		//IE7, Firefox, Safari etc
		return new XMLHttpRequest();
	else
		return false;
}

function basic_ajax_get(url, callback)
{
	var req = get_ajax_object();
	var account = document.getElementById("account").value;
	var password = document.getElementById("password").value;
	var actid = document.getElementById("actorid").value;

	req.onreadystatechange = function() { callback(req); };
	req.open("GET", api + url, true, account, password);
	req.setRequestHeader("X-WoR-Actor", actid);
	req.send("");
}

function get_side_panel(panel_id)
{
	// Get or create a panel in the side-bar(s)
	
    // FIXME: Add persistent client-side storage for user
	// configuration of where panels should go.
	var panel = document.getElementById(panel_id);
	if(!panel)
	{
		var new_panel = "<div id='" + panel_id + "' class='panel'></div>";
		document.getElementById("left_panel").innerHTML += new_panel;
		panel = document.getElementById(panel_id);
	}
	return panel;
}

function parse_input(str)
{
	// Parse a standard key/value input stream, and return an array of the
	// objects read
	var result = new Array();
	var accumulator = new Object();

    var lines = str.split("\n");
    for(var n in lines)
    {
		var line = lines[n];
		var kv = new Array();
		if(line[0] == ' ')
		{
			accumulator[kv[0]] += "\n" + line;
		}
		else if(line == '-')
		{
			result.push(accumulator);
			accumulator = new Object();
			hasdata = false;
		}
		else if(line == '')
		{ }
		else
		{
			kv = line.split(":", 2);
			accumulator[kv[0]] = kv[1];
			hasdata = true;
		}
    }

    if(hasdata)
	{
		result.push(accumulator);
	}
	return result;
}

function parse_input_table(str, cols)
{
	var result = new Array();

	var lines = str.split("\n");
	var row = new Array();
	for(var i in lines)
	{
		var line = lines[i];
		if(line[0] == ' ')
		{
			row[cols-1] += line + "\n";
		}
		else if(line == '')
		{ }
		else
		{
			if(row.length > 0)
				result.push(row);

			// JavaScript's split() method isn't actually sane when
			// given a limit. It splits the whole string, then returns
			// only the first n elements, discarding the remainder.

			// Therefore, we split an unlimited number of elements
			// here, and then splice the ones on the end back
			// together.

			row = line.split(':');
			last_elt = row.slice(cols-1).join(':');
			row.splice(cols-1,row.length,last_elt);
		}
	}

	if(row.length > 0)
	{
		result.push(row);
	}
	return result;
}

function lpad(str, padding, len)
{
	str = new String(str);
	if(padding.length == 0)
		return str;
	while(str.length < len)
		str = padding.concat(str);
	return str;
}

function format_date_time(when)
{
	var result = "";

	with(when)
	{
		result += getFullYear() + "-";
		result += lpad(getMonth(), "0", 2) + "-";
		result += lpad(getDate(), "0", 2) + " ";
		result += lpad(getHours(), "0", 2) + ":";
		result += lpad(getMinutes(), "0", 2) + ":";
		result += lpad(getSeconds(), "0", 2);
	}
	return result;
}
