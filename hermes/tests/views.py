from django.shortcuts import render, redirect
from .models import TestResult, Profile
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomProfileCreationForm
from .models import Profile


def test_results(request):
    results = TestResult.objects.all()
    return render(request, "results.html", {"results": results})


def index(request):
    return render(request, "index.html")

#TODO: Check if user is an adjudicator
# def is_adjudicator(user):
#     return user.groups.filter(name='Adjudicators').exists()

# # @login_required
# def my_view(request):
#     # Your view logic here
#     return render(request, 'my_template.html')


# # @login_required
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
