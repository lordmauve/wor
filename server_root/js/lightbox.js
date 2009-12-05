function FadeIn(element, opts) {
	var duration = (opts.duration) ? opts.duration: 0.5;
	var to = (opts.to) ? opts.to : 1;
	var delay = parseInt(1000 * ((opts.delay) ? opts.delay : 0.01));

	var t0 = new Date().valueOf() + delay;
	element = $(element);
	element.setStyle({opacity: 0});
	this.nextframe = function () {
		var t = (new Date().valueOf() - t0) / 1000.0;
		if (t > duration) {
			// end
			element.setStyle({opacity: to, display: 'block', visibility: 'visible'});
			if (opts.onAfter)
				opts.onAfter();
		} else {
			var opacity = to * Math.pow(Math.sin((t / duration) * Math.PI * 0.5), 2);
			element.setStyle({opacity: opacity, display: 'block', visibility: 'visible'});
			setTimeout(this.nextframe.bind(this), 20);
		}
	};
	
	setTimeout(this.nextframe.bind(this), delay);
};

var Lightbox = {
	washout: null,
	washout_watcher: null,
	onhide: null,

	show: function (content_element, onhide) {
		var body = document.body;
		content_element = $(content_element);

		var washout = new Element('div', {'id': 'washout'});
		washout.setStyle({
			position: 'fixed',
			opacity: 0.0
		});
		if (/MSIE [3-6]/.match(navigator.appVersion)) {
			washout.setStyle({position: 'absolute'});
			washout.setStyle({top: document.documentElement.scrollTop + 'px'});
		}
		body.appendChild(washout);
		Lightbox.update_washout();
		Lightbox.washout_watcher = setInterval(Lightbox.update_washout, 20);

		new FadeIn('washout', {to: 0.6, duration: 0.2});

		content_element.setStyle({display: 'block', visibility: 'hidden'});
		body.appendChild(content_element);

		content_element.style.position = 'absolute';
		content_element.style.left = (document.documentElement.scrollLeft + document.body.scrollLeft + (document.documentElement.clientWidth - content_element.offsetWidth) / 2) + 'px';
		content_element.style.top = (document.documentElement.scrollTop + document.body.scrollTop + (document.documentElement.clientHeight - content_element.offsetHeight) / 2) + 'px';
		content_element.setStyle({display: 'none', visibility: 'visible'});
		new FadeIn(content_element, {delay: 0.2, duration: 0.2});

		Lightbox.washout = washout;		
		Lightbox.onhide = onhide;

		if (onhide)
			Event.observe(this.washout, 'click', Lightbox.hide);
	},

	update_washout: function () {
		$('washout').setStyle({
			width: document.documentElement.clientWidth + 'px',
			height: document.documentElement.clientHeight + 'px'
		});
	},

	hide: function () {
		Lightbox.finalize();
		if (Lightbox.onhide) {
			Lightbox.onhide();
		}
	},

	finalize: function () {
		Lightbox.washout.remove();
		clearInterval(Lightbox.washout_watcher);
	}
};
