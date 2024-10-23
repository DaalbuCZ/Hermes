from django.urls import path
from . import views

urlpatterns = [
    # path('add/', views.add_test_result, name='add_test_result'),
    path('results/', views.test_results, name='test_results'),
]
