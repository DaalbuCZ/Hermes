from django.urls import path
from . import views

urlpatterns = [
    # path('add/', views.add_test_result, name='add_test_result'),
    path("results/", views.test_results, name="results"),
    path("add_profile/", views.add_profile, name="add_profile"),
    path("profile_list/", views.profile_list, name="profile_list"),
    path("ladder_test/", views.ladder_test_view, name="ladder_test"),
    path("brace_test/", views.brace_test_view, name="brace_test"),
    path("hexagon_test/", views.hexagon_test_view, name="hexagon_test"),
    path("medicimbal_test/", views.medicimbal_test_view, name="medicimbal_test"),
    path("jet_test/", views.jet_test_view, name="jet_test"),
    path("y_test/", views.y_test_view, name="y_test"),
    path("triple_jump_test/", views.triple_jump_test_view, name="triple_jump_test"),
    path("beep_test/", views.beep_test_view, name="beep_test"),
    path(
        "adjudicator_dashboard/",
        views.adjudicator_dashboard,
        name="adjudicator_dashboard",
    ),
    path(
        "recalculate_scores/",
        views.recalculate_scores_view,
        name="recalculate_scores",
    ),
]