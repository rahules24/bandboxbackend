from django.urls import path
from .views import ContactSubmitView

urlpatterns = [
    path('submit/', ContactSubmitView.as_view(), name='contact-submit'),
]
