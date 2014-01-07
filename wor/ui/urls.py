from django.conf.urls import patterns, url

urlpatterns = patterns('wor.ui.views',
    (r'^$', 'login'),
    (r'^game$', 'game'),
    url(r'^register$', 'register', name='register'),
)

urlpatterns += patterns('',
    (r'^assets/(.*)', 'django.views.static.serve', {'document_root': '../server_root/', 'show_indexes': True}),
)

