from django.conf.urls.defaults import *

urlpatterns = patterns('ui.views',
    (r'^$', 'login'),
    (r'^game$', 'game'),
    url(r'^register$', 'register', name='register'),
)

urlpatterns += patterns('', 
    (r'^assets/(.*)', 'django.views.static.serve', {'document_root': '../server_root/', 'show_indexes': True}),
)

