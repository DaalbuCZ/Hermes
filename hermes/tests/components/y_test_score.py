from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult, ActiveTest
from tests.score_tables import quick_calculate, calculate_y_test_index
from django.shortcuts import redirect
from decimal import Decimal
from datetime import datetime


class YTestScoreView(UnicornView):
    template_name = "unicorn/y_test_score.html"
    profile_id = None
    # Left Leg
    ll_front = ""
    ll_left = ""
    ll_right = ""
    # Right Leg
    rl_front = ""
    rl_left = ""
    rl_right = ""
    # Left Arm
    la_left = ""
    la_front = ""
    la_back = ""
    # Right Arm
    ra_right = ""
    ra_front = ""
    ra_back = ""
    # Score
    y_test_score = None
    y_test_index = None
    profiles = []
    active_test = None
    previous_result = None

    def mount(self):
        # Load profiles when component is initialized
        self.profiles = Profile.objects.all()
        self.active_test = ActiveTest.objects.filter(is_active=True).first()
        print("Component mounted with profiles:", len(self.profiles))

    def clean_measurement(self, value):
        # Clean and validate measurement input
        if not value and value != 0:  # Handle empty strings and None
            return None
        try:
            cleaned = float(str(value).strip())
            return cleaned if cleaned >= 0 else None
        except (ValueError, TypeError):
            return None

    def calculate_y_test_score(self):
        # Calculate score whenever any input changes
        if not self.profile_id:
            return

        try:
            profile = Profile.objects.get(id=self.profile_id)
            height = float(profile.height)  # Ensure height is float

            # Clean and prepare measurements
            measurements = []
            for m in [
                self.ll_front,
                self.ll_left,
                self.ll_right,
                self.rl_front,
                self.rl_left,
                self.rl_right,
                self.la_left,
                self.la_front,
                self.la_back,
                self.ra_right,
                self.ra_front,
                self.ra_back,
            ]:
                cleaned = self.clean_measurement(m)
                if cleaned is None:
                    print(f"Invalid measurement: {m}")
                    return
                measurements.append(cleaned)

            # All measurements are valid at this point
            self.y_test_index = calculate_y_test_index(height, *measurements)
            print(f"Calculated Y-Test Index: {self.y_test_index}")

            if self.y_test_index:
                self.y_test_score = quick_calculate(
                    profile.age, profile.gender, "y_test", self.y_test_index
                )
                print(f"Calculated Y-Test Score: {self.y_test_score}")

        except Exception as e:
            print(f"Error calculating score: {e}")
            import traceback

            print(traceback.format_exc())

    def update_profile(self, profile_id):
        # Update profile_id and load existing results if any
        self.profile_id = profile_id

        # Reset all values
        self.ll_front = self.ll_left = self.ll_right = ""
        self.rl_front = self.rl_left = self.rl_right = ""
        self.la_left = self.la_front = self.la_back = ""
        self.ra_right = self.ra_front = self.ra_back = ""
        self.y_test_score = self.y_test_index = None

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Try to get existing test result
                test_result = TestResult.objects.filter(
                    profile=profile, active_test=self.active_test
                ).first()

                if test_result:
                    # Map of component fields to database fields
                    fields = {
                        "ll_front": "y_test_ll_front",
                        "ll_left": "y_test_ll_left",
                        "ll_right": "y_test_ll_right",
                        "rl_front": "y_test_rl_front",
                        "rl_left": "y_test_rl_left",
                        "rl_right": "y_test_rl_right",
                        "la_left": "y_test_la_left",
                        "la_front": "y_test_la_front",
                        "la_back": "y_test_la_back",
                        "ra_right": "y_test_ra_right",
                        "ra_front": "y_test_ra_front",
                        "ra_back": "y_test_ra_back",
                    }

                    # Populate existing values if they exist
                    for component_field, db_field in fields.items():
                        value = getattr(test_result, db_field, None)
                        if value is not None:
                            setattr(self, component_field, str(value))

                    # Calculate scores for existing values
                    self.calculate_y_test_score()
                # Find and display previous test results if they exist
                previous_results = (
                    TestResult.objects.filter(profile=profile)
                    .exclude(id=test_result.id)
                    .order_by("-test_date")
                )
                if previous_results.exists():
                    self.previous_result = previous_results.first()
                    print(
                        f"Previous Test Result - Time 1: {self.previous_result.ladder_time_1}, Time 2: {self.previous_result.ladder_time_2}, Score: {self.previous_result.ladder_score}"
                    )

            except Profile.DoesNotExist:
                print("Selected profile not found")

    def save_results(self):
        # Save the test results to the database
        if not self.profile_id:
            return False

        try:
            profile = Profile.objects.get(id=self.profile_id)
            test_result, created = TestResult.objects.get_or_create(
                profile=profile, active_test=self.active_test
            )

            # Update measurements only if they are valid
            measurements = {
                "y_test_ll_front": self.ll_front,
                "y_test_ll_left": self.ll_left,
                "y_test_ll_right": self.ll_right,
                "y_test_rl_front": self.rl_front,
                "y_test_rl_left": self.rl_left,
                "y_test_rl_right": self.rl_right,
                "y_test_la_left": self.la_left,
                "y_test_la_front": self.la_front,
                "y_test_la_back": self.la_back,
                "y_test_ra_right": self.ra_right,
                "y_test_ra_front": self.ra_front,
                "y_test_ra_back": self.ra_back,
            }

            for field, value in measurements.items():
                cleaned_value = self.clean_measurement(value)
                if cleaned_value is not None:
                    setattr(test_result, field, cleaned_value)

            if self.y_test_score is not None:
                test_result.y_test_score = self.y_test_score
            if self.y_test_index is not None:
                test_result.y_test_index = self.y_test_index

            # Save active test information if available
            if self.active_test:
                test_result.active_test = self.active_test
                test_result.test_name = self.active_test.name
                try:
                    test_result.test_date = datetime.strptime(
                        self.active_test.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).date()  # Convert to date
                except ValueError:
                    test_result.test_date = datetime.strptime(
                        self.active_test.created_at, "%Y-%m-%d %H:%M:%S"
                    ).date()  # Fallback format
                test_result.team = self.active_test.team
            test_result.save()
            return redirect("adjudicator_dashboard")
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
