from django_unicorn.components import UnicornView
from tests.models import Profile
from tests.score_tables import calculate_score


class BeepTestScoreView(UnicornView):
    profile_id = None
    input_value = 0
    score = 0
