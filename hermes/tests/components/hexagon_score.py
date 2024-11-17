from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate
from django.shortcuts import redirect


class HexagonScoreView(UnicornView):
	template_name = "unicorn/hexagon_score.html"
	profile_id = None
	time_cw = 0
	time_ccw = 0
	score_cw = 0
	score_ccw = 0
	profiles = []

	def mount(self):
		"""Load profiles when component is initialized"""
		self.profiles = Profile.objects.all()
		print("Component mounted with profiles:", len(self.profiles))

	def calculate_hexagon_score(self):
		"""Calculate scores whenever inputs change"""
		print(f"Calculating scores - Profile ID: {self.profile_id}, Time CW: {self.time_cw}, Time CCW: {self.time_ccw}")
		
		if self.profile_id:
			try:
				profile = Profile.objects.get(id=self.profile_id)
				if self.time_cw:
					self.score_cw = quick_calculate(
						profile.age, profile.gender, "hexagon", float(self.time_cw)
					)
				if self.time_ccw:
					self.score_ccw = quick_calculate(
						profile.age, profile.gender, "hexagon", float(self.time_ccw)
					)
				print(f"Scores calculated: {self.score_cw}, {self.score_ccw}")
			except (Profile.DoesNotExist, ValueError) as e:
				print(f"Error calculating scores: {e}")
				self.score_cw = 0
				self.score_ccw = 0
		else:
			print("Missing profile_id")

	def update_profile(self, profile_id):
		"""Update profile_id and recalculate scores"""
		self.profile_id = profile_id
		self.calculate_hexagon_score()

	def save_results(self):
		"""Save the test results to the database"""
		if self.profile_id and (self.time_cw or self.time_ccw):
			try:
				profile = Profile.objects.get(id=self.profile_id)
				test_result, created = TestResult.objects.get_or_create(profile=profile)
				
				if self.time_cw:
					test_result.hexagon_time_cw = float(self.time_cw)
				if self.time_ccw:
					test_result.hexagon_time_ccw = float(self.time_ccw)
				
				test_result.hexagon_score = max(self.score_cw, self.score_ccw)
				test_result.save()
				
				return redirect("adjudicator_dashboard")
			except Exception as e:
				print(f"Error saving results: {e}")
				return False
		return False