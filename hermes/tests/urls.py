from django.urls import path
from . import views

urlpatterns = [
    # path('add/', views.add_test_result, name='add_test_result'),
    path("results/", views.test_results, name="test_results"),
    path("add_profile/", views.add_profile, name="add_profile"),
    path('profile_list/', views.profile_list, name='profile_list'),
]
