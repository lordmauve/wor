////////////
// Main function: Called to initiate loading the page contents

function load_game()
{
  var player_req = get_ajax_object();
  var api = "http://" + document.domain + "/api";

  player_req.onreadystatechange = function() { load_basic_player(player_req); };
  player_req.open("GET", api + "/player", true,
		  "darksatanic", "wor");
  player_req.send("");

  var player_act_req = get_ajax_object();
  player_act_req.onreadystatechange = function() { load_player_act(player_act_req); };
  player_act_req.open("GET", api + "/player/act", true,
		      "darksatanic", "wor");
  player_act_req.send("");
}

////////////
// Library functions

function get_ajax_object()
{
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
