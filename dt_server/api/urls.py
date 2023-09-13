from django.urls import path
from api import views as api_views

urlpatterns = [
    path('categories/', api_views.categories, name='categories'),    
    path('categories_hierarchy/', api_views.categories_hierarchy, name='categories_hierarchy'),    
]