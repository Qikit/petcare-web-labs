from django.urls import path

from . import views

urlpatterns = [
    path('', views.service_list, name='service-list'),
    path('add/', views.service_create, name='service-create'),
    path('<int:pk>/', views.service_detail, name='service-detail'),
    path('<int:pk>/edit/', views.service_edit, name='service-edit'),
    path('<int:pk>/delete/', views.service_delete, name='service-delete'),
]
