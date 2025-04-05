from ninja import NinjaAPI, Schema
from typing import List
from datetime import date, datetime, timedelta
from .models import Profile, TestResult, ActiveTest, Team
from django.shortcuts import get_object_or_404
from ninja.security import HttpBearer
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

SECRET_KEY = settings.SECRET_KEY


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("username")
            if username:
                return username
        except jwt.PyJWTError:
            return None


api = NinjaAPI(auth=AuthBearer())


# Auth Schemas
class TokenSchema(Schema):
    token: str


class AuthSchema(Schema):
    username: str
    password: str


# Other Schemas
class ProfileSchema(Schema):
    id: int | None = None  # Make id optional for creation
    name: str
    surname: str
    date_of_birth: date
    gender: str
    height: float
    weight: float


class TestResultSchema(Schema):
    id: int
    profile_id: int
    test_date: date
    test_name: str
    team: str | None

    # Composite scores
    agility_score: float | None
    endurance_score: float | None
    speed_score: float | None
    strength_score: float | None

    # Ladder test
    ladder_score: float | None
    ladder_time_1: float | None
    ladder_time_2: float | None

    # Hexagon test
    hexagon_score: int | None
    hexagon_time_cw: float | None
    hexagon_time_ccw: float | None

    # Y test
    y_test_score: int | None
    y_test_index: float | None
    y_test_ll_front: float | None
    y_test_ll_left: float | None
    y_test_ll_right: float | None
    y_test_rl_front: float | None
    y_test_rl_right: float | None
    y_test_rl_left: float | None
    y_test_la_left: float | None
    y_test_la_front: float | None
    y_test_la_back: float | None
    y_test_ra_right: float | None
    y_test_ra_front: float | None
    y_test_ra_back: float | None

    # Brace test
    brace_score: int | None
    brace_time_1: float | None
    brace_time_2: float | None

    # Medicimbal test
    medicimbal_score: int | None
    medicimbal_throw_1: float | None
    medicimbal_throw_2: float | None
    medicimbal_throw_3: float | None

    # Jet test
    jet_score: int | None
    jet_laps: int | None
    jet_sides: int | None
    jet_distance: int | None

    # Triple jump test
    triple_jump_score: int | None
    triple_jump_distance_1: float | None
    triple_jump_distance_2: float | None
    triple_jump_distance_3: float | None

    # Beep test
    beep_test_score: int | None
    beep_test_level: int | None
    beep_test_laps: int | None
    beep_test_total_laps: int | None
    max_hr: int | None


class TeamSchema(Schema):
    id: int
    name: str
    created_at: date


# Additional schemas
class ActiveTestSchema(Schema):
    id: int
    name: str
    is_active: bool
    created_at: datetime
    team_id: int | None
    created_by_id: int | None


class UserSchema(Schema):
    id: int
    username: str
    is_active: bool
    teams: List[int]  # List of team IDs


# Auth endpoints
@api.post("/token", auth=None, response=TokenSchema)
def get_token(request, auth_data: AuthSchema):
    user = authenticate(username=auth_data.username, password=auth_data.password)
    if user is None:
        return api.create_response(
            request, {"detail": "Invalid credentials"}, status=401
        )

    token = jwt.encode(
        {
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    return {"token": token}


# Existing endpoints
@api.get("/profiles", response=List[ProfileSchema])
def get_profiles(request):
    return Profile.objects.all()


@api.get("/profile/{profile_id}", response=ProfileSchema)
def get_profile(request, profile_id: int):
    return get_object_or_404(Profile, id=profile_id)


@api.get("/results", response=List[TestResultSchema])
def get_test_results(request):
    return TestResult.objects.all()


@api.get("/results/{profile_id}", response=List[TestResultSchema])
def get_profile_results(request, profile_id: int):
    return TestResult.objects.filter(profile_id=profile_id)


@api.get("/teams", response=List[TeamSchema])
def get_teams(request):
    return Team.objects.all()


@api.get("/team/{team_id}/results", response=List[TestResultSchema])
def get_team_results(request, team_id: int):
    return TestResult.objects.filter(profile__team_id=team_id)


# Profile endpoints
@api.post("/profiles", response=ProfileSchema)
def create_profile(request, profile: ProfileSchema):
    profile_data = profile.dict(exclude={"id"})  # Exclude id when creating
    return Profile.objects.create(**profile_data)


@api.put("/profile/{profile_id}", response=ProfileSchema)
def update_profile(request, profile_id: int, profile: ProfileSchema):
    profile_obj = get_object_or_404(Profile, id=profile_id)
    for key, value in profile.dict(exclude_unset=True).items():
        setattr(profile_obj, key, value)
    profile_obj.save()
    return profile_obj


@api.delete("/profile/{profile_id}")
def delete_profile(request, profile_id: int):
    profile = get_object_or_404(Profile, id=profile_id)
    profile.delete()
    return {"success": True}


# Test result endpoints
@api.post("/results", response=TestResultSchema)
def create_test_result(request, test_result: TestResultSchema):
    profile = get_object_or_404(Profile, id=test_result.profile_id)
    return TestResult.objects.create(
        profile=profile, **test_result.dict(exclude={"profile_id"})
    )


@api.put("/results/{result_id}", response=TestResultSchema)
def update_test_result(request, result_id: int, test_result: TestResultSchema):
    result = get_object_or_404(TestResult, id=result_id)
    for key, value in test_result.dict(
        exclude_unset=True, exclude={"profile_id"}
    ).items():
        setattr(result, key, value)
    result.save()
    return result


@api.delete("/results/{result_id}")
def delete_test_result(request, result_id: int):
    result = get_object_or_404(TestResult, id=result_id)
    result.delete()
    return {"success": True}


# Team management endpoints
@api.post("/teams", response=TeamSchema)
def create_team(request, team: TeamSchema):
    return Team.objects.create(**team.dict())


@api.put("/team/{team_id}", response=TeamSchema)
def update_team(request, team_id: int, team: TeamSchema):
    team_obj = get_object_or_404(Team, id=team_id)
    for key, value in team.dict(exclude_unset=True).items():
        setattr(team_obj, key, value)
    team_obj.save()
    return team_obj


@api.delete("/team/{team_id}")
def delete_team(request, team_id: int):
    team = get_object_or_404(Team, id=team_id)
    team.delete()
    return {"success": True}


# Additional test result queries
@api.get("/results/latest/{profile_id}", response=TestResultSchema)
def get_latest_profile_result(request, profile_id: int):
    return (
        TestResult.objects.filter(profile_id=profile_id).order_by("-test_date").first()
    )


@api.get("/results/team/{team_id}/latest", response=List[TestResultSchema])
def get_team_latest_results(request, team_id: int):
    return (
        TestResult.objects.filter(profile__team_id=team_id)
        .order_by("profile_id", "-test_date")
        .distinct("profile_id")
    )


@api.get("/results/aggregate/{profile_id}")
def get_profile_aggregate_scores(request, profile_id: int):
    latest_result = (
        TestResult.objects.filter(profile_id=profile_id).order_by("-test_date").first()
    )
    if not latest_result:
        return {"detail": "No test results found"}
    return {
        "strength_score": latest_result.strength_score,
        "speed_score": latest_result.speed_score,
        "endurance_score": latest_result.endurance_score,
        "agility_score": latest_result.agility_score,
    }


# Active test management endpoints
@api.get("/active-tests", response=List[ActiveTestSchema])
def get_active_tests(request):
    """Get all active tests, filtered by user's teams if not superuser"""
    if request.auth.is_superuser:
        return ActiveTest.objects.all()
    return ActiveTest.objects.filter(team__in=request.auth.teams.all())


@api.get("/active-tests/{team_id}", response=List[ActiveTestSchema])
def get_team_active_tests(request, team_id: int):
    """Get active tests for a specific team"""
    return ActiveTest.objects.filter(team_id=team_id)


@api.post("/active-tests", response=ActiveTestSchema)
def create_active_test(request, active_test: ActiveTestSchema):
    """Create a new active test"""
    # Deactivate all other tests for the team if this one is active
    if active_test.is_active and active_test.team_id:
        ActiveTest.objects.filter(team_id=active_test.team_id, is_active=True).update(
            is_active=False
        )
    return ActiveTest.objects.create(**active_test.dict())


@api.put("/active-tests/{test_id}", response=ActiveTestSchema)
def update_active_test(request, test_id: int, active_test: ActiveTestSchema):
    """Update an active test"""
    test_obj = get_object_or_404(ActiveTest, id=test_id)
    if active_test.is_active and active_test.team_id:
        # Deactivate other tests only if we're activating this one
        if not test_obj.is_active:
            ActiveTest.objects.filter(
                team_id=active_test.team_id, is_active=True
            ).update(is_active=False)
    for key, value in active_test.dict(exclude_unset=True).items():
        setattr(test_obj, key, value)
    test_obj.save()
    return test_obj


@api.delete("/active-tests/{test_id}")
def delete_active_test(request, test_id: int):
    """Delete an active test"""
    test = get_object_or_404(ActiveTest, id=test_id)
    test.delete()
    return {"success": True}


# User management endpoints
@api.get("/users", response=List[UserSchema])
def get_users(request):
    """Get all users - requires superuser"""
    if not request.auth.is_superuser:
        return api.create_response(request, {"detail": "Not authorized"}, status=403)
    return User.objects.all()


@api.get("/users/adjudicators", response=List[UserSchema])
def get_adjudicators(request):
    """Get all adjudicators"""
    return User.objects.filter(groups__name="Adjudicators")


@api.get("/users/me", response=UserSchema)
def get_current_user(request):
    """Get current user's information"""
    return request.auth


@api.put("/users/me/teams", response=UserSchema)
def update_user_teams(request, team_ids: List[int]):
    """Update teams for the current user"""
    user = request.auth
    user.teams.set(team_ids)
    return user


# Test type specific endpoints
@api.get("/results/test-type/{test_type}", response=List[TestResultSchema])
def get_results_by_test_type(request, test_type: str):
    """Get results filtered by test type"""
    field_name = f"{test_type}_score"
    return TestResult.objects.exclude(**{field_name: None})


@api.get(
    "/results/test-type/{test_type}/team/{team_id}", response=List[TestResultSchema]
)
def get_team_results_by_test_type(request, test_type: str, team_id: int):
    """Get team results filtered by test type"""
    field_name = f"{test_type}_score"
    return TestResult.objects.filter(profile__team_id=team_id).exclude(
        **{field_name: None}
    )


@api.get(
    "/results/test-type/{test_type}/profile/{profile_id}",
    response=List[TestResultSchema],
)
def get_profile_results_by_test_type(request, test_type: str, profile_id: int):
    """Get profile results filtered by test type"""
    field_name = f"{test_type}_score"
    return TestResult.objects.filter(profile_id=profile_id).exclude(
        **{field_name: None}
    )


# Statistics endpoints
@api.get("/statistics/team/{team_id}")
def get_team_statistics(request, team_id: int):
    """Get statistical summary of all test results for a team"""
    from django.db.models import Avg, Max, Min

    test_types = [
        "ladder",
        "hexagon",
        "y_test",
        "brace",
        "medicimbal",
        "jet",
        "triple_jump",
        "beep_test",
    ]

    stats = {}
    for test_type in test_types:
        field_name = f"{test_type}_score"
        results = TestResult.objects.filter(profile__team_id=team_id).exclude(
            **{field_name: None}
        )
        stats[test_type] = {
            "avg_score": results.aggregate(Avg(field_name))[f"{field_name}__avg"],
            "max_score": results.aggregate(Max(field_name))[f"{field_name}__max"],
            "min_score": results.aggregate(Min(field_name))[f"{field_name}__min"],
            "total_tests": results.count(),
        }

    # Add composite scores
    composite_scores = ["strength", "speed", "endurance", "agility"]
    for score_type in composite_scores:
        field_name = f"{score_type}_score"
        results = TestResult.objects.filter(profile__team_id=team_id).exclude(
            **{field_name: None}
        )
        stats[f"{score_type}_composite"] = {
            "avg_score": results.aggregate(Avg(field_name))[f"{field_name}__avg"],
            "max_score": results.aggregate(Max(field_name))[f"{field_name}__max"],
            "min_score": results.aggregate(Min(field_name))[f"{field_name}__min"],
        }

    return stats


@api.get("/statistics/profile/{profile_id}")
def get_profile_progress(request, profile_id: int):
    """Get progress statistics for a profile across all test types"""
    from django.db.models import F

    test_types = [
        "ladder",
        "hexagon",
        "y_test",
        "brace",
        "medicimbal",
        "jet",
        "triple_jump",
        "beep_test",
    ]

    progress = {}
    for test_type in test_types:
        field_name = f"{test_type}_score"
        results = (
            TestResult.objects.filter(profile_id=profile_id)
            .exclude(**{field_name: None})
            .order_by("test_date")
            .values("test_date", field_name)
        )

        if len(results) >= 2:
            first_score = results.first()[field_name]
            last_score = results.last()[field_name]
            progress[test_type] = {
                "improvement": last_score - first_score,
                "improvement_percentage": (
                    ((last_score - first_score) / first_score * 100)
                    if first_score
                    else None
                ),
                "scores_over_time": [
                    {"date": r["test_date"], "score": r[field_name]} for r in results
                ],
            }

    return progress
