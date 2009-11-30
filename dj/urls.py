from django.conf.urls.defaults import *

urlpatterns = patterns('api_views',
	(r'^api/actors$', 'actors'),
	(r'^api/items/names$', 'item_names'),
	(r'^api/items/names/(\w+)', 'item_names'),

	(r'^api/actor/(?P<target>\d+)/(?P<op>desc|inventory|equipment)', 'actor_detail'),
	(r'^api/actor/(?P<target>\d+)/log', 'actor_log'),
	(r'^api/actor/self/(?P<op>desc|inventory|equipment)', 'actor_detail'),
	(r'^api/actor/self/actions', 'actions'),
	(r'^api/actor/self/log', 'actor_log'),

	(r'^api/location/(?P<location_id>\d+)/(?P<op>desc|actions)', 'location'),
	(r'^api/location/here/(?P<op>desc|actions)', 'location'),
	(r'^api/location/neighbourhood', 'neighbourhood'),

	(r'^api/item/(\d+)/desc', 'item'),
)

urlpatterns += patterns('', 
	(r'(.*)', 'django.views.static.serve', {'document_root': '../server_root/', 'show_indexes': True}),
)
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^dj/', include('dj.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
