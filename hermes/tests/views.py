from django.shortcuts import render, redirect, get_object_or_404
from .models import TestResult, Profile
from django.contrib.auth.decorators import login_required, user_passes_test
from .score_tables import calculate_score, calculate_beep_test_total_laps
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
)


def test_results(request):
    results = TestResult.objects.all()
    return render(request, "results.html", {"results": results})


def index(request):
    return render(request, "index.html")


# TODO: Check if user is an adjudicator
# def is_adjudicator(user):
#     return user.groups.filter(name='Adjudicators').exists()

# @login_required
# def my_view(request):
#     # Your view logic here
#     return render(request, 'my_template.html')


# @login_required
# @user_passes_test(is_adjudicator)
def add_profile(request):
    if request.method == "POST":
        form = CustomProfileCreationForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)  # Don't save yet
            profile.save()  # Explicitly save the profile
            return redirect("profile_list")

    else:
        form = CustomProfileCreationForm()

    return render(request, "add_profile.html", {"form": form})


def profile_list(request):
    profiles = Profile.objects.all()
    return render(request, "profile_list.html", {"profiles": profiles})


def ladder_test_view(request):
    if request.method == "POST":
        form = LadderForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            time_1 = test_result.ladder_time_1
            time_2 = test_result.ladder_time_2

            score = calculate_score(age, sex, "ladder", time_1, time_2)
            test_result.ladder_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = LadderForm()
    profiles = Profile.objects.all()
    return render(request, "ladder_test.html", {"form": form, "profiles": profiles})


def brace_test_view(request):
    if request.method == "POST":
        form = BraceForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            time_1 = test_result.brace_time_1
            time_2 = test_result.brace_time_2

            score = calculate_score(age, sex, "brace", time_1, time_2)
            test_result.brace_score = score
            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = BraceForm()
    profiles = Profile.objects.all()
    return render(request, "brace_test.html", {"form": form, "profiles": profiles})


def hexagon_test_view(request):
    if request.method == "POST":
        form = HexagonForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            time_cw = test_result.hexagon_time_cw
            time_ccw = test_result.hexagon_time_ccw

            score = calculate_score(age, sex, "hexagon", time_cw, time_ccw)
            test_result.hexagon_score = score

            test_result.save()
            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = HexagonForm()
    profiles = Profile.objects.all()
    return render(request, "hexagon_test.html", {"form": form, "profiles": profiles})


def medicimbal_test_view(request):
    if request.method == "POST":
        form = MedicimbalForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            throw_1 = test_result.medicimbal_throw_1
            throw_2 = test_result.medicimbal_throw_2
            throw_3 = test_result.medicimbal_throw_3

            score = calculate_score(age, sex, "medicimbal", throw_1, throw_2, throw_3)
            test_result.medicimbal_score = score

            test_result.save()
            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = MedicimbalForm()
    profiles = Profile.objects.all()
    return render(request, "medicimbal_test.html", {"form": form, "profiles": profiles})


def jet_test_view(request):
    if request.method == "POST":
        form = JetForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            test_result.jet_distance = (
                test_result.jet_laps * 40 + test_result.jet_sides * 10
            )

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            distance = test_result.jet_distance

            score = calculate_score(age, sex, "jet", distance)
            test_result.jet_score = score

            test_result.save()
            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = JetForm()
    profiles = Profile.objects.all()
    return render(request, "jet_test.html", {"form": form, "profiles": profiles})


def y_test_view(request):
    if request.method == "POST":
        form = YTestForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            height = test_result.profile.height
            ll_front = test_result.y_test_ll_front
            ll_left = test_result.y_test_ll_left
            ll_right = test_result.y_test_ll_right
            rl_front = test_result.y_test_rl_front
            rl_right = test_result.y_test_rl_right
            rl_left = test_result.y_test_rl_left
            la_left = test_result.y_test_la_left
            la_front = test_result.y_test_la_front
            la_back = test_result.y_test_la_back
            ra_right = test_result.y_test_ra_right
            ra_front = test_result.y_test_ra_front
            ra_back = test_result.y_test_ra_back

            score = calculate_score(
                age,
                sex,
                "y_test",
                height,
                ll_front,
                ll_left,
                ll_right,
                rl_front,
                rl_right,
                rl_left,
                la_left,
                la_front,
                la_back,
                ra_right,
                ra_front,
                ra_back,
            )
            test_result.y_test_score = score

            test_result.save()
            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = YTestForm()
    profiles = Profile.objects.all()
    return render(request, "y_test.html", {"form": form, "profiles": profiles})


def beep_test_view(request):
    if request.method == "POST":
        form = BeepTestForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            laps = test_result.beep_test_laps
            level = test_result.beep_test_level
            total_laps = calculate_beep_test_total_laps(level, laps)

            score = calculate_score(age, sex, "beep_test", total_laps)
            test_result.beep_test_score = score

            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = BeepTestForm()
    profiles = Profile.objects.all()
    return render(request, "beep_test.html", {"form": form, "profiles": profiles})


def triple_jump_test_view(request):
    if request.method == "POST":
        form = TripleJumpForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            test_result.profile = get_object_or_404(Profile, id=profile_id)

            # Calculate score
            age = test_result.profile.age
            sex = test_result.profile.sex
            jump_1 = test_result.triple_jump_distance_1
            jump_2 = test_result.triple_jump_distance_2
            jump_3 = test_result.triple_jump_distance_3

            score = calculate_score(age, sex, "medicimbal", jump_1, jump_2, jump_3)
            test_result.medicimbal_score = score

            test_result.save()
            return redirect("adjudicator_dashboard")
    else:
        form = TripleJumpForm()
    profiles = Profile.objects.all()
    return render(
        request, "triple_jump_test.html", {"form": form, "profiles": profiles}
    )


def adjudicator_dashboard(request):
    return render(request, "adjudicator_dashboard.html")
