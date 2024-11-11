from django_unicorn.components import UnicornView
from tests.models import Profile
from tests.score_tables import quick_calculate


class LadderScoreView(UnicornView):
    template_name = "unicorn/ladder_score.html"
    profile_id = None
    input_value = 0
    score = 0
    profiles = []

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def calculate_ladder_score(self):
        """Calculate score whenever input changes"""
        print(
            f"Calculating score - Profile ID: {self.profile_id}, Input: {self.input_value}"
        )

        if self.profile_id and self.input_value:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                input_value = float(self.input_value)
                print(f"Profile found - Age: {profile.age}, Gender: {profile.gender}")

                self.score = quick_calculate(
                    profile.age, profile.gender, "ladder", input_value
                )
                print(f"Score calculated: {self.score}")

            except (Profile.DoesNotExist, ValueError) as e:
                print(f"Error calculating score: {e}")
                self.score = 0
        else:
            print("Missing profile_id or input_value")
