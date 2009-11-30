from django.conf.urls.defaults import *

urlpatterns = patterns('ui.views',
	(r'^login$', 'login'),
	(r'^game$', 'game'),
)

urlpatterns += patterns('', 
	(r'^assets/(.*)', 'django.views.static.serve', {'document_root': '../server_root/', 'show_indexes': True}),
)

