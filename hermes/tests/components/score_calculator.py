from django_unicorn.components import UnicornView
from tests.models import Profile
from tests.score_tables import calculate_score


class ScoreCalculatorView(UnicornView):
    profile_id = None
    input_value = 0
    score = 0

    def calculate_ladder_score(self):
        profile = Profile.objects.get(id=self.profile_id)
        age = profile.age
        gender = profile.gender
        self.score = calculate_score(age, gender, "ladder", self.input_value)

    def calculate_brace_score(self):
        profile = Profile.objects.get(id=self.profile_id)
        age = profile.age
        gender = profile.gender
        self.score = calculate_score(age, gender, "brace", self.input_value)

    def calculate_hexagon_score(self):
        profile = Profile.objects.get(id=self.profile_id)
        age = profile.age
        gender = profile.gender
        self.score = calculate_score(age, gender, "hexagon", self.input_value)

    def calculate_medicimbal_score(self):
        profile = Profile.objects.get(id=self.profile_id)
        age = profile.age
        gender = profile.gender
        self.score = calculate_score(age, gender, "medicimbal", self.input_value)

    def calculate_triple_jump_score(self):
        profile = Profile.objects.get(id=self.profile_id)
        age = profile.age
        gender = profile.gender
        self.score = calculate_score(age, gender, "triple_jump", self.input_value)

    # def calculate_jet_score(self):
    #     profile = Profile.objects.get(id=self.profile_id)
    #     age = profile.age
    #     gender = profile.gender
    #     self.score = calculate_score(age, gender, "jet", self.input_value)

    # def calculate_y_test_score(self):
    #     profile = Profile.objects.get(id=self.profile_id)
    #     age = profile.age
    #     gender = profile.gender
    #     self.score = calculate_score(age, gender, "y_test", self.input_value)

    # def calculate_beep_test_score(self):
    #     profile = Profile.objects.get(id=self.profile_id)
    #     age = profile.age
    #     gender = profile.gender
    #     self.score = calculate_score(age, gender, "beep_test", self.input_value)
