from django.conf.urls.defaults import *

urlpatterns = patterns('api_views',
    (r'^api/actors$', 'actors'),
    (r'^api/items/names$', 'item_names'),
    (r'^api/items/names/(\w+)', 'item_names'),

    (r'^api/actor/(?P<target>\d+)/(?P<op>desc|inventory|equipment)', 'actor_detail'),
    (r'^api/actor/(?P<target>\d+)/log', 'actor_log'),
    (r'^api/actor/self/inventory', 'inventory'),
    (r'^api/actor/self/(?P<op>desc|inventory|equipment)', 'actor_detail'),
    (r'^api/actor/self/actions', 'actions'),
    (r'^api/actor/self/log', 'actor_log'),

    (r'^api/location/(?P<location_id>\d+)/(?P<op>desc|actions)', 'location'),
    (r'^api/location/here/(?P<op>desc|actions)', 'location'),
    (r'^api/location/neighbourhood', 'neighbourhood'),

    (r'^api/item/(\d+)/desc', 'item'),

    (r'^', include('ui.urls')),
    (r'^editor/', include('editor.urls')),
)

urlpatterns += patterns('', 
    (r'(.*)', 'django.views.static.serve', {'document_root': '../server_root/', 'show_indexes': True}),
)
