from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers


@api_view(['GET'])
@permission_classes([AllowAny])
@method_decorator(cache_page(3600), name='dispatch')
@vary_on_headers('User-Agent')
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'AmaderFoodie API is running',
        'version': '1.0.0',
        'environment': settings.DEBUG and 'development' or 'production'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """API information endpoint"""
    return Response({
        'name': 'AmaderFoodie API',
        'version': '1.0.0',
        'description': 'API for AmaderFoodie - A community-driven food recipe and blogging platform',
        'endpoints': {
            'authentication': '/api/auth/',
            'recipes': '/api/recipes/',
            'blogs': '/api/blogs/',
            'payments': '/api/payments/',
            'health': '/api/health/'
        },
        'documentation': 'https://docs.amaderfoodie.com/api'
    })