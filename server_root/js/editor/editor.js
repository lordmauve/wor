var EditorPane = {
	init: function () {
		var map_layer = $('map-layer');
		new DragAndDrop.Controller(map_layer);
		var mo = /(-?\d+),(-?\d+)/.exec(location.hash)
		if (mo) {
			var x = parseInt(mo[1], 10);
			var y = parseInt(mo[2], 10);
			map_layer.setStyle({
				left: (map_layer.offsetLeft - x) + 'px',
				top: (map_layer.offsetTop - y) + 'px',
			});
		}
	},
};

Event.observe(window, 'load', EditorPane.init);
