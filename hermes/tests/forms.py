from django import forms
from .models import TestResult, Profile


class CustomProfileCreationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["person_name", "age", "weight", "height", "sex"]


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
        fields = ["hexagon_time_r", "hexagon_time_l"]


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
            "y_test_lf_front",
            "y_test_lf_left",
            "y_test_lf_right",
            "y_test_rf_front",
            "y_test_rf_right",
            "y_test_rf_left",
            "y_test_la_left",
            "y_test_la_front",
            "y_test_la_back",
            "y_test_ra_right",
            "y_test_ra_front",
            "y_test_ra_back",
        ]
