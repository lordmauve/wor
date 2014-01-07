////////////
// Main function: Called to initiate loading the page contents

var api = "/api";

function load_game()
{
    Player.update();
    update_player_actions();
    Map.update();
    MessagePane.update();
}

Event.observe(document, 'dom:loaded', load_game);

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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].replace(/^\s*|\s*$/, '');
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function basic_ajax_get(url, callback)
{
    var req = get_ajax_object();
    var account = document.getElementById("account").value;
    var password = document.getElementById("password").value;
    var actid = document.getElementById("actorid").value;
    var csrftoken = getCookie('csrftoken');

    req.onreadystatechange = function() { callback(req); };
    req.open("GET", api + url, true, account, password);
    req.setRequestHeader("X-CSRFToken", csrftoken);
    req.setRequestHeader("X-WoR-Actor", actid);
    req.send("");
}

function get_json(url, callback, postdata)
{
    var req = get_ajax_object();
    var actid = document.getElementById("actorid").value;
    var csrftoken = getCookie('csrftoken');

    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            if (req.status == 200) {
                if (typeof JSON !== 'undefined') {
                    var arg = JSON.parse(req.responseText);
                } else {
                    var arg = eval('(' + req.responseText + ')');
                }
                //firebug doesn't catch errors in XHR events?
                //so queue event on a short timer
                setTimeout(function () {callback(arg);}, 10)
            } else {
                handle_api_error(req);
            }
        }
    };

    if (postdata) {
        req.open("POST", api + url, true);
        req.setRequestHeader("X-WoR-Actor", actid);
        req.setRequestHeader("X-CSRFToken", csrftoken);
        req.setRequestHeader("Content-Type", 'application/x-www-form-urlencoded');
        req.send(postdata);
    } else {
        req.open("GET", api + url, true);
        req.setRequestHeader("X-WoR-Actor", actid);
        req.setRequestHeader("X-CSRFToken", csrftoken);
        req.send();
    }
}

function handle_api_error(req) {
    var container = new Element('div', {id: 'api-error'}).update('<h3>API Error</h3>');
    container.insert(new Element('div', {id: 'response-wrapper'}).update(req.responseText));
    document.body.insert(container);
}

function get_side_panel(panel_id)
{
    // Get or create a panel in the side-bar(s)

        // FIXME: Add persistent client-side storage for user
    // configuration of where panels should go.
    var panel = $(panel_id);
    if (!panel)
    {
        panel = new Element('div', {id: panel_id, 'class': 'panel'});
        $('panel').insert(panel);
    }
    return panel;
}


function ordinal(num) {
    if (num % 10 == 1 && num % 100 != 11)
        return num + 'st';
    else if (num % 10 == 2 && num % 100 != 12)
        return num + 'nd';
    else if (num % 10 == 3 && num % 100 != 13)
        return num + 'rd';
    return num + 'th';
}

String.prototype.padLeft = function (len, char) {
    var s = this;
    while (s.length < len)
        s = char + s;
    return s;
};

MONTH_NAMES = ['January', 'Februrary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

Date.prototype.toLocaleDateString = function () {
    var month_names = MONTH_NAMES;
    return ordinal(this.getDate()) + ' ' + month_names[this.getMonth()] + ' ' + this.getFullYear();
};

Date.prototype.toLocaleTimeString = function () {
    var h = this.getHours();
    if (h >= 12)
        var suffix = 'pm';
    else
        var suffix = 'am';

    if (h > 12)
        h -= 12;
    else if (h == 0)
        h = 12;

    return h + ':' + new String(this.getMinutes()).padLeft(2, '0') + suffix;
};

Date.prototype.toLocaleString = function () {
    return this.toLocaleDateString() + ' ' + this.toLocaleTimeString();
};

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
