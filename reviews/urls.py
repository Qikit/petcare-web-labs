from django.urls import path

from . import views

urlpatterns = [
    path('appointment/<int:appointment_pk>/', views.review_create, name='review-create'),
]
