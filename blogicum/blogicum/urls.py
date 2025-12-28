from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from blog import views
from django.conf.urls.static import static

handler404 = "pages.views.custom_404_view"
handler403 = "pages.views.custom_403_view"
handler500 = 'pages.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/registration/', views.registration, name='registration'),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
