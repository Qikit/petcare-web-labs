from django.urls import path
from . import views

urlpatterns = [
    path('doctor/<int:doctor_pk>/', views.review_create, name='review-create'),
]
