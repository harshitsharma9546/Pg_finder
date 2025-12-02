from django.urls import path
from . import views

urlpatterns = [
  path('search/', views.search, name='search'),
  path('', views.pgs, name='pgs'),
  path('pgregister/', views.pg_register, name='pg_register'),
  path('<slug:pg_slug>/', views.pg_detail, name='pg_detail'),
]
 