////////////
// Main function: Called to initiate loading the page contents

var api = "http://" + document.domain + "/api";

function load_game()
{
	update_player_details();
	update_player_actions();
}

function update_player_details()
{
  var player_req = get_ajax_object();

  player_req.onreadystatechange = function() { load_basic_player(player_req); };
  player_req.open("GET", api + "/actor/self/desc", true,
		  "darksatanic", "wor");
  player_req.setRequestHeader("X-WoR-Actor", "1")
  player_req.send("");
}

function update_player_actions()
{
  var player_act_req = get_ajax_object();
  player_act_req.onreadystatechange = function() { load_player_act(player_act_req); };
  player_act_req.open("GET", api + "/actor/self/actions", true,
		      "darksatanic", "wor");
  player_act_req.setRequestHeader("X-WoR-Actor", "1")
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
