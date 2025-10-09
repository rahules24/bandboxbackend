from django.urls import path
from .views import BillCreateView
from django.http import JsonResponse

def test_endpoint(request):
    return JsonResponse({"status": "API is reachable"})

urlpatterns = [
    path('', test_endpoint),  # handles /api/bills/
    path('create/', BillCreateView.as_view(), name='create-bill'),
]
