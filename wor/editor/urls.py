from django.conf.urls.defaults import *

urlpatterns = patterns('editor.views',
	(r'^$', 'regions'),
	(r'^(?P<region_id>[^/]+)/$', 'edit_region'),
	(r'^(?P<region_id>[^/]+)/(?P<x>-?\d+),(?P<y>-?\d+)/$', 'edit_location'),
	(r'^(?P<region_id>[^/]+)/new/(?P<x>-?\d+),(?P<y>-?\d+)/$', 'new_location'),
)

