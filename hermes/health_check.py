"""
Health check endpoint for Docker containers
"""
from django.http import HttpResponse
from django.db import connection
from django.db.utils import OperationalError


def health_check(request):
    """
    Health check endpoint that verifies:
    1. Django is running
    2. Database connection is working
    3. Basic functionality is operational
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Return success response
        return HttpResponse("OK", content_type="text/plain", status=200)
    
    except OperationalError:
        # Database connection failed
        return HttpResponse("Database connection failed", content_type="text/plain", status=503)
    
    except Exception as e:
        # Other errors
        return HttpResponse(f"Health check failed: {str(e)}", content_type="text/plain", status=500) 