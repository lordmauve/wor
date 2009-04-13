////////////
// Base player state
function load_basic_player(req)
{
  if(req.readyState == 4)
  {
    if(req.status == 200)
    {
      // Success! Create a Player object
      var p = new Player(req.responseText);
      // Set up the first panel: Basic player info
      var top_panel = document.getElementById("top_panel");

      panel = "<table><tr>";
      panel += "<td class='header'><b>" + p.username + "</b></td>";
      panel += "<td class='header'>AP " + p.ap + "/" + p.maxap + "</td>";
      panel += "<td class='header'>HP " + p.hp + "/" + p.maxhp + "</td>";
      panel += "</tr></table>";

      top_panel.innerHTML = panel;
    }
    else
    {
      // Error here: Server didn't return 200
      top_panel.innerHTML = "Error loading player details.\n<div>" + req.responseText + "</div>";
    }
  }
}

////////////
// Player-specific actions
function load_player_act(req)
{
  if(req.readyState == 4)
  {
    var panel = document.getElementById("player_actions");
    if(!panel)
    {
      document.getElementById("left_panel").innerHTML += "<div id='player_action' class='panel'></div>";
      panel = document.getElementById("player_action");
    }

    if(req.status == 200)
      // Content is basically what we need: render it directly
      panel.innerHTML += req.responseText;
    else
      // Error here: No 200 response
      panel.innerHTML += "Error loading actions.\n<div>" + req.responseText + "</div>";
  }
}

function Player(str)
{
  var lines = str.split("\n");
  for(var n in lines)
  {
    var line = lines[n];
    var kv = line.split(":", 2);
    this[kv[0]] = kv[1];
  }
  
  // Set up other things here, from properties with known internal
  // structure that we want to unpack.
}

Player.prototype.fn = function() { };
