from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken.views import obtain_auth_token
from project.api import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', views.UserViewSet)
router.register(r'part-categories', views.PartCategoryViewSet)
router.register(r'parts', views.PartViewSet)
router.register(r'colors', views.ColorViewSet)
router.register(r'elements', views.ElementViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'me/elements', views.UserElementViewSet)
router.register(r'me/parts', views.UserPartsViewSet, base_name='user-parts')

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', include_docs_urls(title='API title')),
    path('auth-token/', obtain_auth_token)
]
