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

		items.sort(function(a,b) {
					if(a.cls == b.cls) return 0;
					if(a.cls < b.cls) return -1;
					return 1;
				});

		panel.insert(new Element('h3').update('Inventory'));

		var eventlistener = Inventory.onclick.bindAsEventListener(this);

		var objectsection = new Element('div', {'id': 'inventory-items'});
                panel.insert(objectsection);
		for (var i = 0; i < items.length; i++){
			var item = items[i];
                        var div = new Element('div', {'class': 'item'});
                        objectsection.insert(div);
		        var obj_tree = new CollapsibleTree(div, item.name);

                        if (item.description && item.description != item.name) {
                            item.description.split('\n\n').each(function (para) {
                                var p = new Element('p', {'class': 'description'});
                                p.appendChild(document.createTextNode(para));
                                obj_tree.insert(p);
                            });
                        }

                        $A(item.actions).each(function (act) {
                                new Action(act, obj_tree);
                        });
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
