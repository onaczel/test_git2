from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^apps/', include('apps.urls', namespace="apps")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuario/', include('apps.urls')),
    url(r'^privado/', include('apps.urls')),
    url(r'^privadoNoadmin/', include('apps.urls')),
    url(r'^cerrar/', include('apps.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)