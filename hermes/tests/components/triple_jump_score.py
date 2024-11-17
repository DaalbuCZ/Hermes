from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate
from django.shortcuts import redirect


class TripleJumpScoreView(UnicornView):
	template_name = "unicorn/triple_jump_score.html"
	profile_id = None
	distance_1 = 0
	distance_2 = 0
	distance_3 = 0
	score_1 = 0
	score_2 = 0
	score_3 = 0
	profiles = []

	def mount(self):
		"""Load profiles when component is initialized"""
		self.profiles = Profile.objects.all()
		print("Component mounted with profiles:", len(self.profiles))

	def calculate_triple_jump_score(self):
		"""Calculate scores whenever inputs change"""
		print(
			f"Calculating scores - Profile ID: {self.profile_id}, Distances: {self.distance_1}, {self.distance_2}, {self.distance_3}"
		)

		if self.profile_id:
			try:
				profile = Profile.objects.get(id=self.profile_id)
				if self.distance_1:
					self.score_1 = quick_calculate(
						profile.age, profile.gender, "triple_jump", float(self.distance_1)
					)
				if self.distance_2:
					self.score_2 = quick_calculate(
						profile.age, profile.gender, "triple_jump", float(self.distance_2)
					)
				if self.distance_3:
					self.score_3 = quick_calculate(
						profile.age, profile.gender, "triple_jump", float(self.distance_3)
					)
				print(f"Scores calculated: {self.score_1}, {self.score_2}, {self.score_3}")
			except (Profile.DoesNotExist, ValueError) as e:
				print(f"Error calculating scores: {e}")
				self.score_1 = self.score_2 = self.score_3 = 0
		else:
			print("Missing profile_id")

	def update_profile(self, profile_id):
		"""Update profile_id and recalculate scores"""
		self.profile_id = profile_id
		self.calculate_triple_jump_score()

	def save_results(self):
		"""Save the test results to the database"""
		if self.profile_id and (self.distance_1 or self.distance_2 or self.distance_3):
			try:
				profile = Profile.objects.get(id=self.profile_id)
				test_result, created = TestResult.objects.get_or_create(profile=profile)

				if self.distance_1:
					test_result.triple_jump_distance_1 = float(self.distance_1)
				if self.distance_2:
					test_result.triple_jump_distance_2 = float(self.distance_2)
				if self.distance_3:
					test_result.triple_jump_distance_3 = float(self.distance_3)

				test_result.triple_jump_score = max(self.score_1, self.score_2, self.score_3)
				test_result.save()

				return redirect("adjudicator_dashboard")
			except Exception as e:
				print(f"Error saving results: {e}")
				return False
		return False