from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import calculate_score
from django.shortcuts import redirect


class JetScoreView(UnicornView):
    template_name = "unicorn/jet_score.html"
    profile_id = None
    laps = ""
    sides = ""
    distance = None
    score = None
    profiles = []

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def calculate_jet_score(self):
        """Calculate score whenever inputs change"""
        if not self.profile_id:
            return

        try:
            profile = Profile.objects.get(id=int(self.profile_id))

            if (
                self.laps
                and self.sides
                and str(self.laps).strip()
                and str(self.sides).strip()
            ):
                laps = int(self.laps)
                sides = int(self.sides)
                self.distance = laps * 40 + sides * 10

                if self.distance:
                    self.score = calculate_score(
                        profile.age, profile.gender, "jet", self.distance
                    )
                    print(f"Score calculated: {self.score}, Distance: {self.distance}")

        except (Profile.DoesNotExist, ValueError) as e:
            print(f"Error calculating score: {e}")
            self.score = None
            self.distance = None

    def update_profile(self, profile_id):
        """Update profile_id and recalculate score"""
        self.profile_id = str(profile_id)
        self.calculate_jet_score()

    def save_results(self):
        """Save the test results to the database"""
        if not self.profile_id:
            return False

        try:
            profile = Profile.objects.get(id=int(self.profile_id))
            test_result, created = TestResult.objects.get_or_create(profile=profile)

            if self.laps and self.sides:
                test_result.jet_laps = int(self.laps)
                test_result.jet_sides = int(self.sides)
            if self.distance:
                test_result.jet_distance = self.distance
            if self.score:
                test_result.jet_score = self.score

            test_result.save()
            return redirect("adjudicator_dashboard")
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
