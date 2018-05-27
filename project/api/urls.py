from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from project.api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'part-categories', views.PartCategoryViewSet)
router.register(r'parts', views.PartViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', include_docs_urls(title='API title'))
]
