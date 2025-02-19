from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from io import BytesIO
from .models import ActiveTest, Team
from django.contrib.auth.models import User, Group
from .radarplot_generator import generate_radar_plot_from_scores
from .pdf_report_generator import generate_test_results_pdf
from reportlab.platypus import PageBreak
from .models import TestResult, Profile
from django.contrib.auth.decorators import login_required, user_passes_test
from .score_tables import (
    calculate_score,
    calculate_beep_test_total_laps,
    calculate_y_test_index,
)
from .forms import (
    CustomProfileCreationForm,
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


@login_required
@user_passes_test(is_adjudicator)
def test_results(request):
    profiles = Profile.objects.all().order_by("surname")
    profiles = Profile.objects.filter(team__in=request.user.teams.all())

    # Create a list of dictionaries containing profile information and test results
    results = []
    for profile in profiles:
        test_result = TestResult.objects.filter(profile=profile).first()
        results.append({"profile": profile, "test_result": test_result})

    return render(request, "results.html", {"results": results})


def index(request):
    return render(request, "index.html")


@login_required
@user_passes_test(is_adjudicator)
def add_profile(request):
    if request.method == "POST":
        form = CustomProfileCreationForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.created_by = request.user  # Set the creator

            # If user is part of a team with active test, assign the team
            user_teams = request.user.teams.all()
            active_test = ActiveTest.objects.filter(
                is_active=True, team__in=user_teams
            ).first()

            if active_test:
                profile.team = active_test.team

            profile.save()

            # Check if TestResult already exists for this profile and active test
            test_result, created = TestResult.objects.get_or_create(
                profile=profile,
                active_test=active_test,
                defaults={
                    "team": profile.team,
                    "test_name": active_test.name if active_test else None,
                    "test_date": active_test.created_at if active_test else None,
                },
            )

            return redirect("profile_list")
    else:
        form = CustomProfileCreationForm()

    return render(request, "add_profile.html", {"form": form})


@login_required
@user_passes_test(is_adjudicator)
def edit_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == "POST":
        form = CustomProfileCreationForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_list")
    else:
        form = CustomProfileCreationForm(instance=profile)
    return render(request, "edit_profile.html", {"form": form})


@login_required
@user_passes_test(is_adjudicator)
def profile_list(request):
    profiles = Profile.objects.all().order_by("surname")
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(request, "profile_list.html", {"profiles": profiles})


def get_or_create_test_result(profile, test_type, **kwargs):
    test_result, created = TestResult.objects.get_or_create(
        profile=profile,
        defaults=kwargs,
    )
    if not created:
        for key, value in kwargs.items():
            setattr(test_result, key, value)
    return test_result


@login_required
@user_passes_test(is_adjudicator)
def ladder_test_view(request):
    if request.method == "POST":
        form = LadderForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            ladder_time_1 = request.POST.get("ladder_time_1")
            ladder_time_2 = request.POST.get("ladder_time_2")
            test_result = get_or_create_test_result(
                profile,
                "ladder",
                ladder_time_1=float(ladder_time_1) if ladder_time_1 else None,
                ladder_time_2=float(ladder_time_2) if ladder_time_2 else None,
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            score = calculate_score(
                age,
                gender,
                "ladder",
                test_result.ladder_time_1,
                test_result.ladder_time_2,
            )
            test_result.ladder_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = LadderForm()
        profiles = Profile.objects.filter(team__in=request.user.teams.all())
        test_result = None
        profile_id = request.GET.get("profile_id")
        if profile_id:
            profile = get_object_or_404(Profile, id=profile_id)
            test_result = TestResult.objects.filter(profile=profile).first()
    teams = Team.objects.all()
    active_test = ActiveTest.objects.filter(is_active=True).first()
    return render(
        request,
        "tests/ladder_test.html",
        {
            "form": form,
            "profiles": profiles,
            "test_result": test_result,
            "teams": teams,
            "active_test": active_test,
        },
    )


@login_required
@user_passes_test(is_adjudicator)
def brace_test_view(request):
    if request.method == "POST":
        form = BraceForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            brace_time_1 = request.POST.get("brace_time_1")
            brace_time_2 = request.POST.get("brace_time_2")
            test_result = get_or_create_test_result(
                profile,
                "brace",
                brace_time_1=float(brace_time_1) if brace_time_1 else None,
                brace_time_2=float(brace_time_2) if brace_time_2 else None,
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            score = calculate_score(
                age, gender, "brace", test_result.brace_time_1, test_result.brace_time_2
            )
            test_result.brace_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = BraceForm()
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(
        request,
        "tests/brace_test.html",
        {"form": form, "profiles": profiles},
    )


@login_required
@user_passes_test(is_adjudicator)
def hexagon_test_view(request):
    if request.method == "POST":
        form = HexagonForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            hexagon_time_cw = request.POST.get("hexagon_time_cw")
            hexagon_time_ccw = request.POST.get("hexagon_time_ccw")
            test_result = get_or_create_test_result(
                profile,
                "hexagon",
                hexagon_time_cw=float(hexagon_time_cw) if hexagon_time_cw else None,
                hexagon_time_ccw=float(hexagon_time_ccw) if hexagon_time_ccw else None,
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            score = calculate_score(
                age,
                gender,
                "hexagon",
                test_result.hexagon_time_cw,
                test_result.hexagon_time_ccw,
            )
            test_result.hexagon_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = HexagonForm()
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(
        request,
        "tests/hexagon_test.html",
        {"form": form, "profiles": profiles},
    )


@login_required
@user_passes_test(is_adjudicator)
def medicimbal_test_view(request):
    if request.method == "POST":
        form = MedicimbalForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            medicimbal_throw_1 = request.POST.get("medicimbal_throw_1")
            medicimbal_throw_2 = request.POST.get("medicimbal_throw_2")
            medicimbal_throw_3 = request.POST.get("medicimbal_throw_3")
            test_result = get_or_create_test_result(
                profile,
                "medicimbal",
                medicimbal_throw_1=(
                    float(medicimbal_throw_1) if medicimbal_throw_1 else None
                ),
                medicimbal_throw_2=(
                    float(medicimbal_throw_2) if medicimbal_throw_2 else None
                ),
                medicimbal_throw_3=(
                    float(medicimbal_throw_3) if medicimbal_throw_3 else None
                ),
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            score = calculate_score(
                age,
                gender,
                "medicimbal",
                test_result.medicimbal_throw_1,
                test_result.medicimbal_throw_2,
                test_result.medicimbal_throw_3,
            )
            test_result.medicimbal_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = MedicimbalForm()
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(
        request,
        "tests/medicimbal_test.html",
        {"form": form, "profiles": profiles},
    )


@login_required
@user_passes_test(is_adjudicator)
def jet_test_view(request):
    if request.method == "POST":
        form = JetForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            jet_laps = int(request.POST.get("jet_laps"))
            jet_sides = int(request.POST.get("jet_sides"))
            test_result = get_or_create_test_result(
                profile,
                "jet",
                jet_laps=jet_laps,
                jet_sides=jet_sides,
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            jet_distance = jet_laps * 40 + jet_sides * 10
            score = calculate_score(age, gender, "jet", jet_distance)
            test_result.jet_score = score
            test_result.jet_distance = jet_distance
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = JetForm()
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(request, "tests/jet_test.html", {"form": form, "profiles": profiles})


@login_required
@user_passes_test(is_adjudicator)
def y_test_view(request):
    if request.method == "POST":
        form = YTestForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            test_result = get_or_create_test_result(
                profile,
                "y_test",
                y_test_ll_front=float(request.POST.get("y_test_ll_front")),
                y_test_ll_left=float(request.POST.get("y_test_ll_left")),
                y_test_ll_right=float(request.POST.get("y_test_ll_right")),
                y_test_rl_front=float(request.POST.get("y_test_rl_front")),
                y_test_rl_left=float(request.POST.get("y_test_rl_left")),
                y_test_rl_right=float(request.POST.get("y_test_rl_right")),
                y_test_la_left=float(request.POST.get("y_test_la_left")),
                y_test_la_front=float(request.POST.get("y_test_la_front")),
                y_test_la_back=float(request.POST.get("y_test_la_back")),
                y_test_ra_right=float(request.POST.get("y_test_ra_right")),
                y_test_ra_front=float(request.POST.get("y_test_ra_front")),
                y_test_ra_back=float(request.POST.get("y_test_ra_back")),
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            height = test_result.profile.height
            score = calculate_score(
                age,
                gender,
                "y_test",
                height,
                test_result.y_test_ll_front,
                test_result.y_test_ll_left,
                test_result.y_test_ll_right,
                test_result.y_test_rl_front,
                test_result.y_test_rl_left,
                test_result.y_test_rl_right,
                test_result.y_test_la_left,
                test_result.y_test_la_front,
                test_result.y_test_la_back,
                test_result.y_test_ra_right,
                test_result.y_test_ra_front,
                test_result.y_test_ra_back,
            )
            test_result.y_test_score = score
            test_result.y_test_index = calculate_y_test_index(
                height,
                test_result.y_test_ll_front,
                test_result.y_test_ll_left,
                test_result.y_test_ll_right,
                test_result.y_test_rl_front,
                test_result.y_test_rl_left,
                test_result.y_test_rl_right,
                test_result.y_test_la_left,
                test_result.y_test_la_front,
                test_result.y_test_la_back,
                test_result.y_test_ra_right,
                test_result.y_test_ra_front,
                test_result.y_test_ra_back,
            )
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = YTestForm()
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(request, "tests/y_test.html", {"form": form, "profiles": profiles})


@login_required
@user_passes_test(is_adjudicator)
def beep_test_view(request):
    if request.method == "POST":
        form = BeepTestForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            beep_test_laps = int(request.POST.get("beep_test_laps"))
            beep_test_level = int(request.POST.get("beep_test_level"))
            max_hr = int(request.POST.get("max_hr"))
            test_result = get_or_create_test_result(
                profile,
                "beep_test",
                beep_test_laps=beep_test_laps,
                beep_test_level=beep_test_level,
                max_hr=max_hr,
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            total_laps = calculate_beep_test_total_laps(beep_test_level, beep_test_laps)
            score = calculate_score(age, gender, "beep_test", total_laps)
            test_result.beep_test_score = score
            test_result.beep_test_total_laps = total_laps
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = BeepTestForm()
    # Filter profiles by the adjudicator's team
    adjudicator_teams = request.user.teams.all()
    profiles = Profile.objects.filter(team__in=adjudicator_teams)
    return render(request, "tests/beep_test.html", {"form": form, "profiles": profiles})


@login_required
@user_passes_test(is_adjudicator)
def triple_jump_test_view(request):
    if request.method == "POST":
        form = TripleJumpForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            triple_jump_distance = float(request.POST.get("triple_jump_distance"))
            test_result = get_or_create_test_result(
                profile,
                "triple_jump",
                triple_jump_distance=triple_jump_distance,
                active_test=ActiveTest.objects.filter(is_active=True).first(),
            )
            age = test_result.profile.age
            gender = test_result.profile.gender
            score = calculate_score(age, gender, "triple_jump", triple_jump_distance)
            test_result.triple_jump_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)  # Debug print form errors
    else:
        form = TripleJumpForm()
    profiles = Profile.objects.filter(team__in=request.user.teams.all())
    return render(
        request,
        "tests/triple_jump_test.html",
        {"form": form, "profiles": profiles},
    )


@login_required
@user_passes_test(is_admin)
def manage_teams(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_team":
            team_name = request.POST.get("team_name")
            team_description = request.POST.get("team_description")
            admin_id = request.POST.get("admin_id")

            team = Team.objects.create(name=team_name, description=team_description)

            # Assign the selected foreign admin to the team
            admin_user = get_object_or_404(User, id=admin_id)
            admin_user.teams.add(team)

        elif action == "delete_team":
            team_id = request.POST.get("team_id")
            Team.objects.filter(id=team_id).delete()

        return redirect("manage_teams")

    # Get all users who are foreign admins
    foreign_admins = User.objects.filter(groups__name="Foreign Admin")
    teams = Team.objects.all()

    return render(
        request,
        "admin/manage_teams.html",
        {"foreign_admins": foreign_admins, "teams": teams},
    )


def assign_team_and_test_details(team, active_test):
    # Get all adjudicators in the team
    from django.db.models import Q

    adjudicators = (
        User.objects.filter(teams=team)
        .filter(Q(groups__name="Adjudicators") | Q(groups__name="Foreign Admin"))
        .distinct()
    )

    # Update all profiles created by these adjudicators
    for adjudicator in adjudicators:
        # Assign team to adjudicator's profiles
        Profile.objects.filter(created_by=adjudicator).update(team=team)

        # Get profiles created by this adjudicator
        profiles = Profile.objects.filter(created_by=adjudicator)

        # Create new test results for each profile if not already exists
        for profile in profiles:
            TestResult.objects.get_or_create(
                profile=profile,
                active_test=active_test,
                defaults={
                    "team": team,
                    "test_name": active_test.name,
                    "test_date": active_test.created_at,
                },
            )


@login_required
@user_passes_test(is_foreign_admin)
def manage_active_tests(request):
    if request.method == "POST":
        test_id = request.POST.get("test_id")
        team_id = request.POST.get("team_id")
        action = request.POST.get("action")

        if action == "activate":
            # Deactivate all other tests for the team
            ActiveTest.objects.filter(is_active=True, team_id=team_id).update(
                is_active=False
            )

            # Activate the selected test
            active_test = ActiveTest.objects.get(id=test_id)
            active_test.is_active = True
            active_test.save()

            # Assign team and test details
            if active_test.team:
                assign_team_and_test_details(active_test.team, active_test)

        elif action == "add":
            test_name = request.POST.get("test_name")
            team_id = request.POST.get("team_id")
            team = get_object_or_404(Team, id=team_id)

            # Deactivate all other tests for the team
            ActiveTest.objects.filter(is_active=True, team=team).update(is_active=False)

            # Create new active test
            active_test = ActiveTest.objects.create(
                name=test_name, team=team, is_active=True, created_by=request.user
            )

            # Assign team and test details
            assign_team_and_test_details(team, active_test)

        return redirect("manage_active_tests")

    # Get teams accessible to the current user
    if request.user.is_superuser:
        teams = Team.objects.all()
    else:
        teams = request.user.teams.all()

    active_tests = ActiveTest.objects.filter(team__in=teams).order_by("-created_at")
    return render(
        request,
        "admin/manage_tests.html",
        {"active_tests": active_tests, "teams": teams},
    )


@login_required
@user_passes_test(is_adjudicator)
def adjudicator_dashboard(request):
    user_teams = request.user.teams.all()
    active_test = ActiveTest.objects.filter(is_active=True, team__in=user_teams).first()
    return render(request, "adjudicator_dashboard.html", {"active_test": active_test})


@login_required
@user_passes_test(is_adjudicator)
def recalculate_scores_view(request):
    # First recalculate all scores
    recalculate_scores(request)

    # Get user's teams and active test
    user_teams = request.user.teams.all()
    active_test = ActiveTest.objects.filter(is_active=True, team__in=user_teams).first()

    if active_test:
        # Get test results only for the active test and user's teams
        test_results = TestResult.objects.filter(
            profile__team__in=user_teams, active_test=active_test
        ).order_by("profile__surname")
    else:
        test_results = TestResult.objects.none()

    return render(request, "recalculate_scores.html", {"test_results": test_results})


@login_required
@user_passes_test(is_adjudicator)
def download_radar_plot(request, profile_id):
    test_result = get_object_or_404(TestResult, profile_id=profile_id)

    # Get the last 3 test results for this profile
    historical_results = TestResult.objects.filter(
        profile_id=profile_id,
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
        f'attachment; filename="radar_plot_{profile_id}.png"'
    )
    response.write(plot_buffer.getvalue())

    return response


@login_required
@user_passes_test(is_adjudicator)
def get_profile_data(request):
    profile_id = request.GET.get("profile_id")
    profile = get_object_or_404(Profile, id=profile_id)
    data = {
        "age": profile.age,
        "height": profile.height,
        "weight": profile.weight,
        # Include other fields as needed
    }
    return JsonResponse(data)


@login_required
@user_passes_test(is_adjudicator)
def download_pdf_report(request, profile_id):
    test_result = get_object_or_404(TestResult, profile_id=profile_id)

    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()

    # Generate the PDF, passing the current user as adjudicator
    generate_test_results_pdf(test_result, buffer, request.user)

    # Create the HTTP response with PDF mime type
    buffer.seek(0)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="test_results_{profile_id}.pdf"'
    )
    response.write(buffer.getvalue())

    return response


@login_required
@user_passes_test(is_adjudicator)
def download_all_pdf_reports(request):
    # Get all test results ordered by surname
    test_results = TestResult.objects.all().order_by("profile__surname")

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


@login_required
@user_passes_test(is_foreign_admin)
def manage_adjudicators(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_adjudicator":
            form = AdjudicatorCreationForm(request.POST)
            if form.is_valid():
                # Create user
                user = form.save()
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.save()

                # Assign to adjudicators group
                adjudicator_group = Group.objects.get(name="Adjudicators")
                user.groups.add(adjudicator_group)

                # Assign to the same teams as the foreign admin
                user_teams = request.user.teams.all()
                user.teams.set(user_teams)

                return redirect("manage_adjudicators")

        elif action == "delete_adjudicator":
            adjudicator_id = request.POST.get("adjudicator_id")
            User.objects.filter(id=adjudicator_id, groups__name="Adjudicators").delete()
            return redirect("manage_adjudicators")

    else:
        form = AdjudicatorCreationForm()

    # Get adjudicators for the teams managed by the foreign admin
    user_teams = request.user.teams.all()
    adjudicators = User.objects.filter(
        groups__name="Adjudicators", teams__in=user_teams
    ).distinct()

    return render(
        request,
        "admin/manage_adjudicators.html",
        {
            "form": form,
            "adjudicators": adjudicators,
        },
    )
