from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .radarplot_generator import generate_radar_plot_from_scores
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
)
from .recalculate_scores import recalculate_scores
from django.http import JsonResponse


def get_selected_db(request):
    return request.session.get("selected_db", "default")


def test_results(request):
    profiles = Profile.objects.all().order_by("surname")

    # Create a list of dictionaries containing profile information and test results
    results = []
    for profile in profiles:
        test_result = TestResult.objects.filter(profile=profile).first()
        results.append({"profile": profile, "test_result": test_result})

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


def profile_list(request):
    profiles = Profile.objects.all().order_by("surname")
    return render(request, "profile_list.html", {"profiles": profiles})


def ladder_test_view(request):
    if request.method == "POST":
        form = LadderForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)
            # Retrieve the existing TestResult object if it exists
            try:
                test_result = TestResult.objects.using(get_selected_db(request)).get(
                    profile=profile
                )
            except TestResult.DoesNotExist:
                test_result = TestResult(profile=profile)
            # Update the fields only if new values are provided
            ladder_time_1 = request.POST.get("ladder_time_1")
            ladder_time_2 = request.POST.get("ladder_time_2")
            if ladder_time_1:
                test_result.ladder_time_1 = float(ladder_time_1)
            if ladder_time_2:
                test_result.ladder_time_2 = float(ladder_time_2)
            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            time_1 = test_result.ladder_time_1
            time_2 = test_result.ladder_time_2
            score = calculate_score(age, gender, "ladder", time_1, time_2)
            test_result.ladder_score = score
            test_result.save(using=get_selected_db(request))
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)  # Debug print form errors
    else:
        form = LadderForm()
        profiles = Profile.objects.all()
        test_result = None
        profile_id = request.GET.get("profile_id")
        if profile_id:
            profile = get_object_or_404(Profile, id=profile_id)
            try:
                test_result = TestResult.objects.using(get_selected_db(request)).get(
                    profile=profile
                )
            except TestResult.DoesNotExist:
                test_result = None
    return render(
        request,
        "ladder_test.html",
        {"form": form, "profiles": profiles, "test_result": test_result},
    )


def brace_test_view(request):
    if request.method == "POST":
        form = BraceForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)

            # Retrieve the existing TestResult object if it exists
            try:
                test_result = TestResult.objects.using(get_selected_db(request)).get(
                    profile=profile
                )
            except TestResult.DoesNotExist:
                test_result = TestResult(profile=profile)

            # Update the fields only if new values are provided
            brace_time_1 = request.POST.get("brace_time_1")
            brace_time_2 = request.POST.get("brace_time_2")

            if brace_time_1:
                test_result.brace_time_1 = float(brace_time_1)
            if brace_time_2:
                test_result.brace_time_2 = float(brace_time_2)

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            time_1 = test_result.brace_time_1
            time_2 = test_result.brace_time_2
            score = calculate_score(age, gender, "brace", time_1, time_2)
            test_result.brace_score = score

            test_result.save(using=get_selected_db(request))
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)  # Debug print form errors
    else:
        form = BraceForm()
    profiles = Profile.objects.all()
    return render(
        request,
        "brace_test.html",
        {"form": form, "profiles": profiles},
    )


def hexagon_test_view(request):
    if request.method == "POST":
        form = HexagonForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)

            # Retrieve the existing TestResult object if it exists
            try:
                test_result = TestResult.objects.using(get_selected_db(request)).get(
                    profile=profile
                )
            except TestResult.DoesNotExist:
                test_result = TestResult(profile=profile)

            # Update the fields only if new values are provided
            hexagon_time_cw = request.POST.get("hexagon_time_cw")
            hexagon_time_ccw = request.POST.get("hexagon_time_ccw")

            if hexagon_time_cw:
                test_result.hexagon_time_cw = float(hexagon_time_cw)
            if hexagon_time_ccw:
                test_result.hexagon_time_ccw = float(hexagon_time_ccw)

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            time_cw = test_result.hexagon_time_cw
            time_ccw = test_result.hexagon_time_ccw
            score = calculate_score(age, gender, "hexagon", time_cw, time_ccw)
            test_result.hexagon_score = score

            test_result.save(using=get_selected_db(request))
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)  # Debug print form errors
    else:
        form = HexagonForm()
    profiles = Profile.objects.all()
    return render(
        request,
        "hexagon_test.html",
        {"form": form, "profiles": profiles},
    )


def medicimbal_test_view(request):
    if request.method == "POST":
        form = MedicimbalForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)

            # Retrieve the existing TestResult object if it exists
            try:
                test_result = TestResult.objects.using(get_selected_db(request)).get(
                    profile=profile
                )
            except TestResult.DoesNotExist:
                test_result = TestResult(profile=profile)

            # Update the fields only if new values are provided
            medicimbal_throw_1 = request.POST.get("medicimbal_throw_1")
            medicimbal_throw_2 = request.POST.get("medicimbal_throw_2")
            medicimbal_throw_3 = request.POST.get("medicimbal_throw_3")

            if medicimbal_throw_1:
                test_result.medicimbal_throw_1 = float(medicimbal_throw_1)
            if medicimbal_throw_2:
                test_result.medicimbal_throw_2 = float(medicimbal_throw_2)
            if medicimbal_throw_3:
                test_result.medicimbal_throw_3 = float(medicimbal_throw_3)

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            throw_1 = test_result.medicimbal_throw_1
            throw_2 = test_result.medicimbal_throw_2
            throw_3 = test_result.medicimbal_throw_3
            score = calculate_score(
                age, gender, "medicimbal", throw_1, throw_2, throw_3
            )
            test_result.medicimbal_score = score

            test_result.save(using=get_selected_db(request))
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)  # Debug print form errors
    else:
        form = MedicimbalForm()
    profiles = Profile.objects.all()
    return render(
        request,
        "medicimbal_test.html",
        {"form": form, "profiles": profiles},
    )


def jet_test_view(request):
    if request.method == "POST":
        form = JetForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)

            test_result, created = TestResult.objects.update_or_create(
                profile=profile,
                defaults={
                    "jet_laps": int(request.POST.get("jet_laps")),
                    "jet_sides": int(request.POST.get("jet_sides")),
                },
            )

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            laps = test_result.jet_laps
            sides = test_result.jet_sides
            jet_distance = laps * 40 + sides * 10

            if laps is None or sides is None:
                return HttpResponse(
                    "Error: Both jet_laps and jet_sides must be provided", status=400
                )

            score = calculate_score(age, gender, "jet", jet_distance)
            test_result.jet_score = score
            test_result.jet_distance = jet_distance
            test_result.save(using=get_selected_db(request))
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
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
            profile = get_object_or_404(Profile, id=profile_id)

            test_result, created = TestResult.objects.update_or_create(
                profile=profile,
                defaults={
                    "y_test_ll_front": float(request.POST.get("y_test_ll_front")),
                    "y_test_ll_left": float(request.POST.get("y_test_ll_left")),
                    "y_test_ll_right": float(request.POST.get("y_test_ll_right")),
                    "y_test_rl_front": float(request.POST.get("y_test_rl_front")),
                    "y_test_rl_left": float(request.POST.get("y_test_rl_left")),
                    "y_test_rl_right": float(request.POST.get("y_test_rl_right")),
                    "y_test_la_left": float(request.POST.get("y_test_la_left")),
                    "y_test_la_front": float(request.POST.get("y_test_la_front")),
                    "y_test_la_back": float(request.POST.get("y_test_la_back")),
                    "y_test_ra_right": float(request.POST.get("y_test_ra_right")),
                    "y_test_ra_front": float(request.POST.get("y_test_ra_front")),
                    "y_test_ra_back": float(request.POST.get("y_test_ra_back")),
                },
            )

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
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

            if any(
                value is None
                for value in [
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
                    height,
                ]
            ):
                return HttpResponse(
                    "Error: All y_test values must be provided", status=400
                )

            score = calculate_score(
                age,
                gender,
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
            test_result.y_test_index = calculate_y_test_index(
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
            print(test_result.y_test_index)
            print(test_result.y_test_score)
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
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
            profile = get_object_or_404(Profile, id=profile_id)

            test_result, created = TestResult.objects.update_or_create(
                profile=profile,
                defaults={
                    "beep_test_laps": int(request.POST.get("beep_test_laps")),
                    "beep_test_level": int(request.POST.get("beep_test_level")),
                    "max_hr": int(request.POST.get("max_hr")),
                },
            )

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            laps = test_result.beep_test_laps
            level = test_result.beep_test_level
            total_laps = calculate_beep_test_total_laps(level, laps)

            if laps is None or level is None:
                return HttpResponse(
                    "Error: Both beep_test_laps and beep_test_level must be provided",
                    status=400,
                )

            score = calculate_score(age, gender, "beep_test", total_laps)
            test_result.beep_test_score = score
            test_result.beep_test_total_laps = total_laps
            test_result.save()
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)
    else:
        form = BeepTestForm()
    profiles = Profile.objects.all()
    return render(request, "beep_test.html", {"form": form, "profiles": profiles})


def triple_jump_test_view(request):
    if request.method == "POST":
        form = TripleJumpForm(request.POST)
        if form.is_valid():
            profile_id = request.POST.get("profile_id")
            profile = get_object_or_404(Profile, id=profile_id)

            # Retrieve the existing TestResult object if it exists
            try:
                test_result = TestResult.objects.using(get_selected_db(request)).get(
                    profile=profile
                )
            except TestResult.DoesNotExist:
                test_result = TestResult(profile=profile)

            # Update the fields only if new values are provided
            triple_jump_distance = request.POST.get("triple_jump_distance")

            if triple_jump_distance:
                test_result.triple_jump_distance = float(triple_jump_distance)

            # Calculate score
            age = test_result.profile.age
            gender = test_result.profile.gender
            distance = test_result.triple_jump_distance
            score = calculate_score(age, gender, "triple_jump", distance)
            test_result.triple_jump_score = score

            test_result.save(using=get_selected_db(request))
            return redirect("adjudicator_dashboard")
        else:
            print(form.errors)  # Debug print form errors
    else:
        form = TripleJumpForm()
    profiles = Profile.objects.all()
    return render(
        request,
        "triple_jump_test.html",
        {"form": form, "profiles": profiles},
    )


def adjudicator_dashboard(request):
    return render(request, "adjudicator_dashboard.html")


def recalculate_scores_view(request):
    # First recalculate all scores
    recalculate_scores(request)
    
    # Get all test results for display
    test_results = TestResult.objects.all().order_by('profile__surname')
    
    return render(request, 'recalculate_scores.html', {'test_results': test_results})


def download_radar_plot(request, profile_id):
    test_result = get_object_or_404(TestResult, profile_id=profile_id)
    
    # Generate radar plot
    plot_buffer = generate_radar_plot_from_scores(
        test_result.speed_score or 0,
        test_result.endurance_score or 0,
        test_result.agility_score or 0,
        test_result.strength_score or 0
    )
    
    # Create response
    response = HttpResponse(content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="radar_plot_{profile_id}.png"'
    response.write(plot_buffer.getvalue())
    
    return response


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
