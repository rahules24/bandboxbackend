from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BillSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

@method_decorator(ratelimit(key='ip', rate='20/m', block=True), name='dispatch')
class BillCreateView(APIView):
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"POST /api/bills/create/ from {ip} — Data: {request.data}")

        serializer = BillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Bill created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
