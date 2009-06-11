////////////
// Main function: Called to initiate loading the page contents

var api = "http://" + document.domain + "/api";

function load_game()
{
	update_player_details();
	update_player_actions();
	update_messages();
}

function update_player_details()
{
  var player_req = get_ajax_object();
  var account = document.getElementById("account").value
  var password = document.getElementById("password").value
  var actid = document.getElementById("actorid").value

  player_req.onreadystatechange = function() { load_basic_player(player_req); };
  player_req.open("GET", api + "/actor/self/desc", true,
		  account, password);
  player_req.setRequestHeader("X-WoR-Actor", actid);
  player_req.send("");
}

function update_player_actions()
{
  var player_act_req = get_ajax_object();
  var account = document.getElementById("account").value
  var password = document.getElementById("password").value
  var actid = document.getElementById("actorid").value

  player_act_req.onreadystatechange = function() { load_player_act(player_act_req); };
  player_act_req.open("GET", api + "/actor/self/actions", true,
		      account, password);
  player_act_req.setRequestHeader("X-WoR-Actor", actid)
  player_act_req.send("");
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

function format_date_time(when)
{
	var result = "";

	with(when)
	{
		result += getFullYear() + "-" + getMonth() + "-" + getDate();
		result += " " + getHours() + ":" + getMinutes() + ":" + getSeconds();
	}
	return result;
}
