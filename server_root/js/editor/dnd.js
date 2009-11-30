function Point(x, y) {
	this.x=x;
	this.y=y;

	this.add = function (p) {
		return new Point(this.x + p.x, this.y + p.y);
	};

	this.subtract = function (p) {
		return new Point(this.x - p.x, this.y - p.y);
	};

	this.clamp = function (minx, miny, maxx, maxy) {
		if (this.x < minx) this.x = minx;
		if (this.y < miny) this.y = miny;
		if (this.x > maxx) this.x = maxx;
		if (this.y > maxy) this.y = maxy;
	};
}

var DragAndDrop={
	Controller: function (el) {
		this.dragging = false;

		this.getPointerPos = function (evt) {
			return new Point(Event.pointerX(evt), Event.pointerY(evt));
		};
		
		this.startDrag = function (evt) {
			el.parentNode.appendChild(el);	//bring to top
			this.startmouse = this.getPointerPos(evt);
			el.startpos = new Point(el.offsetLeft, el.offsetTop);
			Event.observe(document, 'mousemove', this.drag);
			Event.observe(document, 'mouseup', this.stopDrag);
			Event.stop(evt);
		}.bindAsEventListener(this);

		this.checkClick = function (evt) {
			var cur = this.getPointerPos(evt);
			if (!this.dragging && cur.x == this.startmouse.x && cur.y == this.startmouse.y)
				el.click_handler(evt);
		}.bindAsEventListener(this);

		this.checkLinkClick = function (evt) {
			// links can't be clickable while dragging
			var cur = this.getPointerPos(evt);
			if (this.dragging || cur.x != this.startmouse.x || cur.y != this.startmouse.y)
				Event.stop(evt);
		}.bindAsEventListener(this);

		el.select('a').each(function (x) {
			Event.observe(x, 'click', this.checkLinkClick);
		}.bind(this));

		this.stopDrag = function (evt) {
			Event.stopObserving(document, 'mousemove', this.drag);
			Event.stopObserving(document, 'mouseup', this.stopDrag);
			Event.stop(evt);
			this.onDragStop();
			this.dragging = false;
		}.bindAsEventListener(this);

		this.drag = function (evt) {
			var cur = this.getPointerPos(evt);
			var delta = cur.subtract(this.startmouse);
			if (!this.dragging && delta.x != 0 && delta.y != 0) {
				this.onDragStart();
				this.dragging = true;
			}
			var pos = el.startpos.add(delta)
			el.setStyle({left: pos.x + 'px', top: pos.y + 'px'});
		}.bindAsEventListener(this);

		this.onDragStart = function () {
			el.addClassName('dragging');
		};
		
		this.onDragStop = function () {
			el.removeClassName('dragging');
		}
		Event.observe(el, 'mousedown', this.startDrag);
	}
};
