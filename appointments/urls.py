from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.appointment_create, name='appointment-create'),
    path('', views.appointment_list, name='appointment-list'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment-cancel'),
    path('record/<int:pk>/pdf/', views.medical_record_pdf, name='medical-record-pdf'),
]
