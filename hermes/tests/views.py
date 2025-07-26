from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from io import BytesIO
from .models import Event, Team
from django.contrib.auth.models import User, Group
from .radarplot_generator import generate_radar_plot_from_scores
from .pdf_report_generator import generate_test_results_pdf
from reportlab.platypus import PageBreak
from .models import TestResult, Person
from django.contrib.auth.decorators import login_required, user_passes_test
from .score_tables import (
    calculate_score,
    calculate_beep_test_total_laps,
    calculate_y_test_index,
)
from .forms import (
    CustomPersonCreationForm,
    LadderForm,
    BraceForm,
    HexagonForm,
    MedicimbalForm,
    JetForm,
    YTestForm,
    BeepTestForm,
    TripleJumpForm,
    AdjudicatorCreationForm,
)
from .recalculate_scores import recalculate_scores
from django.http import JsonResponse
from django.contrib import messages


def is_foreign_admin(user):
    return user.is_superuser or user.groups.filter(name="Foreign Admin").exists()


def is_admin(user):
    return user.is_superuser


def is_adjudicator(user):
    return (
        user.groups.filter(name="Adjudicators").exists()
        or user.is_superuser
        or user.groups.filter(name="Foreign Admin").exists()
    )


def get_or_create_test_result(person, test_type, **kwargs):
    test_result, created = TestResult.objects.get_or_create(
        person=person,
        defaults=kwargs,
    )
    if not created:
        for key, value in kwargs.items():
            setattr(test_result, key, value)
    return test_result


@login_required
@user_passes_test(is_adjudicator)
def download_radar_plot(request, person_id):
    test_result = get_object_or_404(TestResult, person_id=person_id)

    # Get the last 3 test results for this profile
    historical_results = TestResult.objects.filter(
        person_id=person_id,
        active_test=test_result.active_test,
        team=test_result.team,
    ).order_by("-test_date")[:3]

    # Remove current test result from historical results if present
    if test_result in historical_results:
        historical_results = list(historical_results)
        historical_results.remove(test_result)
    else:
        historical_results = list(historical_results)[1:]  # Take only previous results

    # Generate radar plot
    plot_buffer = generate_radar_plot_from_scores(
        test_result.speed_score or 0,
        test_result.endurance_score or 0,
        test_result.agility_score or 0,
        test_result.strength_score or 0,
        historical_results=historical_results,
    )

    # Create response
    response = HttpResponse(content_type="image/png")
    response["Content-Disposition"] = (
        f'attachment; filename="radar_plot_{person_id}.png"'
    )
    response.write(plot_buffer.getvalue())

    return response


@login_required
@user_passes_test(is_adjudicator)
def get_person_data(request):
    person_id = request.GET.get("person_id")
    person = get_object_or_404(Person, id=person_id)
    data = {
        "age": person.age,
        "height": person.height,
        "weight": person.weight,
        # Include other fields as needed
    }
    return JsonResponse(data)


@login_required
@user_passes_test(is_adjudicator)
def download_pdf_report(request, person_id):
    test_result = get_object_or_404(TestResult, person_id=person_id)

    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()

    # Generate the PDF, passing the current user as adjudicator
    generate_test_results_pdf(test_result, buffer, request.user)

    # Create the HTTP response with PDF mime type
    buffer.seek(0)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="test_results_{person_id}.pdf"'
    )
    response.write(buffer.getvalue())

    return response


@login_required
@user_passes_test(is_adjudicator)
def download_all_pdf_reports(request):
    # Get all test results ordered by surname
    test_results = TestResult.objects.all().order_by("person__surname")

    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()

    # Generate the PDF with all results, passing the current user as adjudicator
    generate_test_results_pdf(list(test_results), buffer, request.user)

    # Create the HTTP response with PDF mime type
    buffer.seek(0)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="all_test_results.pdf"'
    response.write(buffer.getvalue())

    return response
