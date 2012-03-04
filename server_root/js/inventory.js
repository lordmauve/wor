// Inventory handling

// Start to select an item from the player's inventory

var Inventory = {
	panel: null,

	show: function () {
		var req = get_json("/actor/self/inventory", Inventory.display);
	},

	display: function (items) {
		if (!Inventory.panel) {
			var panel = new Element('div', {'id': 'inventory_panel'});
			Inventory.panel = panel;
		} else {
			var panel = Inventory.panel;
			panel.update('');
		}

	/*	items.sort(function(a,b) {
					if(a[3] == b[3]) return 0;
					if(a[3] < b[3]) return -1;
					return 1;
				});*/

		panel.insert(new Element('h3').update('Inventory'));

		var eventlistener = Inventory.onclick.bindAsEventListener(this);

		for (var i = 0; i < items.length; i++){
			var item = items[i];
			var but = new Element('button');
			but.appendChild(document.createTextNode(item.name));
			panel.insert(but);
			but.item = item;
			but.observe('click', eventlistener);
		}
		
		var close = new Element('img', {'src': '/icons/close.png', id: 'close'});
		panel.insert(close);
		Event.observe(close, 'click', Lightbox.hide);

		Lightbox.show(panel, Inventory.onhide);
	},

	onhide: function () {
		Inventory.panel.remove();
	},

	onclick: function (event)
	{
		Event.stop(event);
		var item = event.element().item;
		get_json('/actor/self/actions/', act_response, 'action=self-change_item&id=' + item.id);
		Lightbox.hide();
	}
};
