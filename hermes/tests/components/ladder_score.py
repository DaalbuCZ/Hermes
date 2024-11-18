from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate, calculate_score
from django.shortcuts import redirect
from django.core.exceptions import ValidationError


class LadderScoreView(UnicornView):
    template_name = "unicorn/ladder_score.html"
    profile_id = None
    time_1 = ""
    time_2 = ""
    score_1 = 0
    score_2 = 0
    profiles = []
    errors = {"time_1": "", "time_2": "", "profile": "", "general": ""}

    def clean_measurement(self, value, field_name):
        """Clean and validate measurement input"""
        if not value and value != 0:  # Handle empty strings and None
            self.errors[field_name] = "This field is required"
            return None
        try:
            cleaned = float(str(value).strip())
            if cleaned < 0:
                self.errors[field_name] = "Time cannot be negative"
                return None
            if cleaned > 100:  # Reasonable maximum time limit
                self.errors[field_name] = "Time seems too high"
                return None
            self.errors[field_name] = ""
            return cleaned
        except (ValueError, TypeError):
            self.errors[field_name] = "Please enter a valid number"
            return None

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def calculate_ladder_score(self):
        """Calculate scores whenever inputs change"""
        self.errors["general"] = ""

        if not self.profile_id:
            self.errors["profile"] = "Please select a profile"
            return

        try:
            profile = Profile.objects.get(id=self.profile_id)
            self.errors["profile"] = ""

            # Clean and validate inputs
            clean_time_1 = self.clean_measurement(self.time_1, "time_1")
            clean_time_2 = self.clean_measurement(self.time_2, "time_2")

            # Reset scores if invalid input
            self.score_1 = 0
            self.score_2 = 0

            if clean_time_1 is not None:
                try:
                    self.score_1 = quick_calculate(
                        profile.age, profile.gender, "ladder", clean_time_1
                    )
                except Exception as e:
                    self.errors["time_1"] = f"Error calculating score: {str(e)}"

            if clean_time_2 is not None:
                try:
                    self.score_2 = quick_calculate(
                        profile.age, profile.gender, "ladder", clean_time_2
                    )
                except Exception as e:
                    self.errors["time_2"] = f"Error calculating score: {str(e)}"

        except Profile.DoesNotExist:
            self.errors["profile"] = "Selected profile not found"
            self.score_1 = 0
            self.score_2 = 0
        except Exception as e:
            self.errors["general"] = f"Error calculating scores: {str(e)}"

    def update_profile(self, profile_id):
        """Update profile_id and recalculate scores"""
        self.profile_id = profile_id
        self.calculate_ladder_score()

    def save_results(self):
        """Save the test results to the database"""
        if not self.profile_id:
            self.errors["profile"] = "Please select a profile"
            return False

        try:
            profile = Profile.objects.get(id=self.profile_id)

            # Validate inputs before saving
            clean_time_1 = self.clean_measurement(self.time_1, "time_1")
            clean_time_2 = self.clean_measurement(self.time_2, "time_2")

            if not clean_time_1 and not clean_time_2:
                self.errors["general"] = (
                    "At least one valid time measurement is required"
                )
                return False

            test_result, created = TestResult.objects.get_or_create(profile=profile)

            if clean_time_1 is not None:
                test_result.ladder_time_1 = clean_time_1
            if clean_time_2 is not None:
                test_result.ladder_time_2 = clean_time_2

            try:
                test_result.ladder_score = calculate_score(
                    profile.age,
                    profile.gender,
                    "ladder",
                    test_result.ladder_time_1,
                    test_result.ladder_time_2,
                )
                test_result.save()
                return redirect("adjudicator_dashboard")
            except ValidationError as e:
                self.errors["general"] = f"Validation error: {str(e)}"
            except Exception as e:
                self.errors["general"] = f"Error calculating final score: {str(e)}"

        except Profile.DoesNotExist:
            self.errors["profile"] = "Selected profile not found"
        except Exception as e:
            self.errors["general"] = f"Error saving results: {str(e)}"

        return False
