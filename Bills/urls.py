from django.urls import path
from .views import BillCreateView

urlpatterns = [
    path('create/', BillCreateView.as_view(), name='create-bill'),
]
