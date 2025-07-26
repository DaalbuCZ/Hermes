from django.urls import path
from . import views

urlpatterns = [
    path("manage-tests/", views.manage_active_tests, name="manage_active_tests"),
    path("manage-teams/", views.manage_teams, name="manage_teams"),
    path("manage-adjudicators/", views.manage_adjudicators, name="manage_adjudicators"),
    path("results/", views.test_results, name="results"),
    path("add_person/", views.add_person, name="add_person"),
    path("person_list/", views.person_list, name="person_list"),
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
    path(
        "download_radar_plot/<int:person_id>/",
        views.download_radar_plot,
        name="download_radar_plot",
    ),
    path("edit_person/<int:person_id>/", views.edit_person, name="edit_person"),
    path("get_person_data/", views.get_person_data, name="get_person_data"),
    path(
        "download-pdf/<int:person_id>/",
        views.download_pdf_report,
        name="download_pdf_report",
    ),
    path(
        "download-all-pdf/",
        views.download_all_pdf_reports,
        name="download_all_pdf_reports",
    ),
]
