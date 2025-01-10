from django import forms
from .models import TestResult, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group


class CustomProfileCreationForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Profile
        fields = ["name", "surname", "date_of_birth", "height", "weight", "gender"]


class LadderForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ["ladder_time_1", "ladder_time_2"]


class BraceForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ["brace_time_1", "brace_time_2"]


class HexagonForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ["hexagon_time_cw", "hexagon_time_ccw"]


class MedicimbalForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ["medicimbal_throw_1", "medicimbal_throw_2", "medicimbal_throw_3"]


class JetForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ["jet_laps", "jet_sides"]


class YTestForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = [
            "y_test_ll_front",
            "y_test_ll_left",
            "y_test_ll_right",
            "y_test_rl_front",
            "y_test_rl_right",
            "y_test_rl_left",
            "y_test_la_left",
            "y_test_la_front",
            "y_test_la_back",
            "y_test_ra_right",
            "y_test_ra_front",
            "y_test_ra_back",
        ]


class TripleJumpForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = [
            "triple_jump_distance_1",
            "triple_jump_distance_2",
            "triple_jump_distance_3",
        ]


class BeepTestForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ["beep_test_level", "beep_test_laps", "max_hr"]


class AdjudicatorCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2")
