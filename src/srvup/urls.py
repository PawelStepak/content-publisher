from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from views import get_api_home, jquery_test_view, home
from videos.views import category_list, category_detail, video_detail
from billing.views import braintree_upgrade, billing_history, braintree_cancel_subscription, payu_upgrade, payu_notify, account_upgrade
from accounts.views import account_dashboard
from comments.views import comment_thread, comment_create_view
from notifications.views import all, get_notifications_ajax, read
from srvup.views import send_feedback

from rest_framework import routers 
from rest_framework_jwt.views import obtain_jwt_token
from videos.serializers import VideoViewSet, CategoryViewSet
from comments.serializers import CommentViewSet
from videos.views import CategoryListAPIView, CategoryDetailAPIView, VideoDetailAPIView
from comments.views import CommentAPICreateView, CommentDetailAPIView, CommentListAPIView

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'videos', VideoViewSet)

urlpatterns = [
    # default API router
    url(r'^api/', include(router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    # in order to get an auth token we need to make curl reqeust (it uses django-rest-framework-jwt/)
    # curl -X POST -d "username=admin&password=abc123" http://localhost:8000/api-token-auth/
    # to get the access with a token: curl -H "Authorization: JWT <your_token>" http://localhost:8000/protected-url/
    url(r'^api/auth/token/$', obtain_jwt_token),

    # Lists all categories we have
    url(r'^api2/categories/$', CategoryListAPIView.as_view(), name='category_list_api'),
    url(r'^api2/categories/(?P<slug>[\w-]+)/$', CategoryDetailAPIView.as_view(), name='category_detail_api'),
    url(r'^api2/categories/(?P<cat_slug>[\w-]+)/(?P<vid_slug>[\w-]+)/$', VideoDetailAPIView.as_view(), name='video_detail_api'),
    url(r'^api2/comment/$', CommentListAPIView.as_view(), name='comment_list_api'),
    url(r'^api2/comment/create/$', CommentAPICreateView.as_view(), name='comment_create_api'),
    url(r'^api2/comment/(?P<id>\d+)/$', CommentDetailAPIView.as_view(), name='comment_detail_api'),

    # new APIs for jquery test
    url(r'^api2/$', get_api_home, name='api_home'),
    url(r'^jquery-test/$', jquery_test_view, name='jquery_test_view'),

    # Project main navigation map
    url(r'^$', home, name='home'),
    url(r'^contact_us/$', TemplateView.as_view(template_name='company/contact_us.html'), name='contact_us'),
    url(r'^categories/$', category_list, name='categories'),
    url(r'^categories/(?P<cat_slug>[\w-]+)/$', category_detail, name='cat_detail'),
    url(r'^categories/(?P<cat_slug>[\w-]+)/(?P<vid_slug>[\w-]+)/$', video_detail, name='video_detail'),
    url(r'^admin/', admin.site.urls),
    url(r'^send_feedback/$', send_feedback, name='send_feedback'),
]
# enrollment
urlpatterns += [
    url(r'^billing/upgrade/$', account_upgrade, name='account_upgrade'),
    url(r'^billing/history/$', billing_history, name='billing_history'),
    url(r'^billing/braintree_upgrade/$', braintree_upgrade, name='braintree_upgrade'),
    url(r'^billing/braintree_cancel$', braintree_cancel_subscription, name='braintree_cancel_subscription'),
    url(r'^billing/payu_upgrade/$', payu_upgrade, name='payu_upgrade'),
    url(r'^billing/payu_notify/$', payu_notify, name='payu_notify'),
]

# auth login/logout/register
urlpatterns += [
    url(r'^accounts/dashbaord/$', account_dashboard, name='account_dashboard'),
    url(r'^accounts/', include('allauth.urls')),
]

# Comment Thread
urlpatterns += [
    url(r'^comments/(?P<id>\d+)/$', comment_thread, name='comment_thread'),
    url(r'^comments/create/$', comment_create_view, name='comment_create'),
]

# Notifications Thread
urlpatterns += [
    url(r'^notifications/$', all, name='notifications_all'),
    url(r'^notifications/ajax/$', get_notifications_ajax, name='get_notifications_ajax'),
    url(r'^notifications/read/(?P<id>\d+)/$', read, name='notifications_read'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)