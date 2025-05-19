from ninja import NinjaAPI, Schema, Body  # Add this import
from typing import List
from datetime import date, datetime, timedelta
from .models import Profile, TestResult, ActiveTest, Team
from django.shortcuts import get_object_or_404
from ninja.security import HttpBearer
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# Add this import
from .score_tables import calculate_score, calculate_beep_test_total_laps, calculate_y_test_index
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test

SECRET_KEY = settings.SECRET_KEY


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("username")
            if username:
                try:
                    user = User.objects.get(username=username)
                    return user  # Return the full User object
                except User.DoesNotExist:
                    return None
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
    team_id: int | None  # <-- Add this line
    age: int  # <-- Add this line


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
    created_at: datetime


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
    is_superuser: bool  # Add superuser status
    teams: List[int]  # List of team IDs
    groups: List[str]  # Add group names


# Schema for creating a new adjudicator
class AdjudicatorSchema(Schema):
    username: str
    password: str
    first_name: str
    last_name: str


def is_superadmin(user):
    return user.is_superuser


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
    # Return each profile as a dict with age
    return [
        {
            "id": p.id,
            "name": p.name,
            "surname": p.surname,
            "date_of_birth": p.date_of_birth,
            "gender": p.gender,
            "height": p.height,
            "weight": p.weight,
            "team_id": p.team.id if p.team else None,
            "age": p.age,
        }
        for p in Profile.objects.all()
    ]


@api.get("/profile/{profile_id}", response=ProfileSchema)
def get_profile(request, profile_id: int):
    return get_object_or_404(Profile, id=profile_id)


@api.get("/results", response=List[TestResultSchema])
def get_test_results(request):
    results = TestResult.objects.all()
    # Serialize team as string (team name) for each result
    serialized = []
    for r in results:
        d = r.__dict__.copy()
        d["team"] = r.team.name if hasattr(r, "team") and r.team else None
        d["profile_id"] = r.profile.id if hasattr(r, "profile") and r.profile else None
        d["test_date"] = r.test_date
        serialized.append(d)
    return serialized


@api.get("/results/{profile_id}", response=List[TestResultSchema])
def get_profile_results(request, profile_id: int):
    return TestResult.objects.filter(profile_id=profile_id)


@api.get("/teams", response=List[TeamSchema])
def get_teams(request):
    if not request.auth or not request.auth.is_superuser:
        return api.create_response(request, {"detail": "Not authorized"}, status=403)
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
    if not request.auth or not request.auth.is_superuser:
        return api.create_response(request, {"detail": "Not authorized"}, status=403)
    return Team.objects.create(**team.dict())


@api.put("/team/{team_id}", response=TeamSchema)
def update_team(request, team_id: int, team: TeamSchema):
    if not request.auth or not request.auth.is_superuser:
        return api.create_response(request, {"detail": "Not authorized"}, status=403)
    team_obj = get_object_or_404(Team, id=team_id)
    for key, value in team.dict(exclude_unset=True).items():
        setattr(team_obj, key, value)
    team_obj.save()
    return team_obj


@api.delete("/team/{team_id}")
def delete_team(request, team_id: int):
    if not request.auth or not request.auth.is_superuser:
        return api.create_response(request, {"detail": "Not authorized"}, status=403)
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
    return ActiveTest.objects.filter(team_id=team_id, is_active=True)


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
    user = request.auth
    if user:
        return UserSchema(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            teams=[team.id for team in user.teams.all()],
            groups=[group.name for group in user.groups.all()],
        )
    return api.create_response(request, {"detail": "Not authenticated"}, status=401)


@api.put("/users/me/teams", response=UserSchema)
def update_user_teams(request, team_ids: List[int]):
    """Update teams for the current user"""
    user = request.auth
    user.teams.set(team_ids)
    return user


@api.post("/users/adjudicators", response=UserSchema)
def add_adjudicator(request, adjudicator: AdjudicatorSchema):
    username = adjudicator.username
    password = adjudicator.password
    first_name = adjudicator.first_name
    last_name = adjudicator.last_name
    if not (username and password and first_name and last_name):
        return api.create_response(request, {"detail": "Missing fields"}, status=400)
    if User.objects.filter(username=username).exists():
        return api.create_response(request, {"detail": "Username already exists"}, status=400)
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )
    group, _ = Group.objects.get_or_create(name="Adjudicators")
    user.groups.add(group)
    user.save()
    return user


@api.delete("/users/adjudicators/{id}")
def delete_adjudicator(request, id: int):
    """Delete an adjudicator by ID"""
    user = get_object_or_404(User, id=id)
    group = Group.objects.get(name="Adjudicators")
    if group in user.groups.all():
        user.delete()
        return {"success": True}
    return api.create_response(request, {"detail": "User is not an adjudicator"}, status=400)


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

# Add these new test-specific endpoints after the existing endpoints
@api.post("/ladder-test/{profile_id}", response=TestResultSchema)
def save_ladder_test(request, profile_id: int, data: dict = Body(...)):
    # print(f"Received ladder test data: {data}")
    # print(f"Data types - time1: {type(data.get('ladder_time_1'))}, time2: {type(data.get('ladder_time_2'))}")
    try:
        if (
            (data.get("ladder_time_1") is not None and not isinstance(data.get("ladder_time_1"), (int, float)))
            or
            (data.get("ladder_time_2") is not None and not isinstance(data.get("ladder_time_2"), (int, float)))
        ):
            return api.create_response(
                request, {"detail": "Invalid times - each time must be a number or null"}, status=422
            )

        profile = get_object_or_404(Profile, id=profile_id)
        # print(f"Profile found - ID: {profile.id}, Age: {profile.age}, Gender: {profile.gender}, Team: {profile.team}")
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        # print(f"Active test found: {active_test is not None}")

        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )

        score = calculate_score(
            profile.age,
            profile.gender,
            "ladder",
            data.get("ladder_time_1"),
            data.get("ladder_time_2")
        )
        # print(f"Calculated score: {score}")

        if score is None:
            return api.create_response(
                request,
                {"detail": "Invalid times - they must be within valid ranges for the athlete's age"},
                status=422
            )

        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "ladder_time_1": data.get("ladder_time_1"),
                "ladder_time_2": data.get("ladder_time_2"),
                "ladder_score": score,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )

        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        # print(f"Error processing ladder test: {str(e)}")
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/brace-test/{profile_id}", response=TestResultSchema)
def save_brace_test(request, profile_id: int, data: dict = Body(...)):
    profile = get_object_or_404(Profile, id=profile_id)
    active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
    
    if not active_test:
        return api.create_response(
            request, {"detail": "No active test found for this profile's team"}, status=400
        )
    
    if (
        (data.get("brace_time_1") is not None and not isinstance(data.get("brace_time_1"), (int, float)))
        or
        (data.get("brace_time_2") is not None and not isinstance(data.get("brace_time_2"), (int, float)))
    ):
        return api.create_response(
            request, {"detail": "Invalid times - each time must be a number or null"}, status=422
        )

    test_result, created = TestResult.objects.update_or_create(
        profile=profile,
        active_test=active_test,
        defaults={
            "brace_time_1": data.get("brace_time_1"),
            "brace_time_2": data.get("brace_time_2"),
            "brace_score": calculate_score(
                profile.age,
                profile.gender,
                "brace",
                data.get("brace_time_1"),
                data.get("brace_time_2")
            ),
            "test_name": active_test.name,
            "test_date": date.today(),
            "team": active_test.team,
        }
    )
    test_result.save()
    from django.forms.models import model_to_dict
    response_data = model_to_dict(test_result)
    response_data["team"] = test_result.team.name if test_result.team else None
    response_data["profile_id"] = test_result.profile.id
    response_data["test_date"] = test_result.test_date
    return response_data

@api.post("/hexagon-test/{profile_id}", response=TestResultSchema)
def save_hexagon_test(request, profile_id: int, data: dict = Body(...)):
    try:
        if (
            (data.get("hexagon_time_cw") is not None and not isinstance(data.get("hexagon_time_cw"), (int, float)))
            or
            (data.get("hexagon_time_ccw") is not None and not isinstance(data.get("hexagon_time_ccw"), (int, float)))
        ):
            return api.create_response(
                request, {"detail": "Invalid times - each time must be a number or null"}, status=422
            )
        profile = get_object_or_404(Profile, id=profile_id)
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        score = calculate_score(
            profile.age,
            profile.gender,
            "hexagon",
            data.get("hexagon_time_cw"),
            data.get("hexagon_time_ccw")
        )
        if score is None:
            return api.create_response(
                request,
                {"detail": "Invalid times - they must be within valid ranges for the athlete's age"},
                status=422
            )
        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "hexagon_time_cw": data.get("hexagon_time_cw"),
                "hexagon_time_ccw": data.get("hexagon_time_ccw"),
                "hexagon_score": score,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/y-test/{profile_id}", response=TestResultSchema)
def save_y_test(request, profile_id: int, data: dict = Body(...)):
    try:
        profile = get_object_or_404(Profile, id=profile_id)
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        y_test_score = calculate_score(
            profile.age,
            profile.gender,
            "y_test",
            profile.height,
            data.get("y_test_ll_front"),
            data.get("y_test_ll_left"),
            data.get("y_test_ll_right"),
            data.get("y_test_rl_front"),
            data.get("y_test_rl_left"),
            data.get("y_test_rl_right"),
            data.get("y_test_la_left"),
            data.get("y_test_la_front"),
            data.get("y_test_la_back"),
            data.get("y_test_ra_right"),
            data.get("y_test_ra_front"),
            data.get("y_test_ra_back")
        )
        y_test_index = calculate_y_test_index(
            profile.height,
            data.get("y_test_ll_front"),
            data.get("y_test_ll_left"),
            data.get("y_test_ll_right"),
            data.get("y_test_rl_front"),
            data.get("y_test_rl_left"),
            data.get("y_test_rl_right"),
            data.get("y_test_la_left"),
            data.get("y_test_la_front"),
            data.get("y_test_la_back"),
            data.get("y_test_ra_right"),
            data.get("y_test_ra_front"),
            data.get("y_test_ra_back")
        )
        if y_test_score is None or y_test_index is None:
            return api.create_response(
                request,
                {"detail": "Invalid Y test values - check input data"},
                status=422
            )
        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "y_test_ll_front": data.get("y_test_ll_front"),
                "y_test_ll_left": data.get("y_test_ll_left"),
                "y_test_ll_right": data.get("y_test_ll_right"),
                "y_test_rl_front": data.get("y_test_rl_front"),
                "y_test_rl_left": data.get("y_test_rl_left"),
                "y_test_rl_right": data.get("y_test_rl_right"),
                "y_test_la_left": data.get("y_test_la_left"),
                "y_test_la_front": data.get("y_test_la_front"),
                "y_test_la_back": data.get("y_test_la_back"),
                "y_test_ra_right": data.get("y_test_ra_right"),
                "y_test_ra_front": data.get("y_test_ra_front"),
                "y_test_ra_back": data.get("y_test_ra_back"),
                "y_test_score": y_test_score,
                "y_test_index": y_test_index,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/medicimbal-test/{profile_id}", response=TestResultSchema)
def save_medicimbal_test(request, profile_id: int, data: dict = Body(...)):
    try:
        for i in [1, 2, 3]:
            val = data.get(f"medicimbal_throw_{i}")
            if val is not None and not isinstance(val, (int, float)):
                return api.create_response(
                    request, {"detail": f"Throw {i} must be a number or null"}, status=422
                )
        profile = get_object_or_404(Profile, id=profile_id)
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        score = calculate_score(
            profile.age,
            profile.gender,
            "medicimbal",
            data.get("medicimbal_throw_1"),
            data.get("medicimbal_throw_2"),
            data.get("medicimbal_throw_3")
        )
        if score is None:
            return api.create_response(
                request,
                {"detail": "Invalid throws - they must be within valid ranges for the athlete's age"},
                status=422
            )
        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "medicimbal_throw_1": data.get("medicimbal_throw_1"),
                "medicimbal_throw_2": data.get("medicimbal_throw_2"),
                "medicimbal_throw_3": data.get("medicimbal_throw_3"),
                "medicimbal_score": score,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/jet-test/{profile_id}", response=TestResultSchema)
def save_jet_test(request, profile_id: int, data: dict = Body(...)):
    try:
        profile = get_object_or_404(Profile, id=profile_id)
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        # Always calculate distance from laps and sides
        jet_laps = data.get("jet_laps")
        jet_sides = data.get("jet_sides")
        if jet_laps is None or jet_sides is None:
            return api.create_response(
                request, {"detail": "jet_laps and jet_sides are required"}, status=422
            )
        jet_distance = jet_laps * 40 + jet_sides * 10
        score = calculate_score(
            profile.age,
            profile.gender,
            "jet",
            jet_distance
        )
        if score is None:
            return api.create_response(
                request,
                {"detail": "Invalid jet test values - check input data"},
                status=422
            )
        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "jet_laps": jet_laps,
                "jet_sides": jet_sides,
                "jet_distance": jet_distance,
                "jet_score": score,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/triple-jump-test/{profile_id}", response=TestResultSchema)
def save_triple_jump_test(request, profile_id: int, data: dict = Body(...)):
    try:
        for i in [1, 2, 3]:
            val = data.get(f"triple_jump_distance_{i}")
            if val is not None and not isinstance(val, (int, float)):
                return api.create_response(
                    request, {"detail": f"Jump distance {i} must be a number or null"}, status=422
                )
        profile = get_object_or_404(Profile, id=profile_id)
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        score = calculate_score(
            profile.age,
            profile.gender,
            "triple_jump",
            data.get("triple_jump_distance_1"),
            data.get("triple_jump_distance_2"),
            data.get("triple_jump_distance_3")
        )
        if score is None:
            return api.create_response(
                request,
                {"detail": "Invalid jump distances - they must be within valid ranges for the athlete's age"},
                status=422
            )
        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "triple_jump_distance_1": data.get("triple_jump_distance_1"),
                "triple_jump_distance_2": data.get("triple_jump_distance_2"),
                "triple_jump_distance_3": data.get("triple_jump_distance_3"),
                "triple_jump_score": score,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/beep-test/{profile_id}", response=TestResultSchema)
def save_beep_test(request, profile_id: int, data: dict = Body(...)):
    try:
        profile = get_object_or_404(Profile, id=profile_id)
        active_test = ActiveTest.objects.filter(is_active=True, team=profile.team).first()
        if not active_test:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        beep_test_level = data.get("beep_test_level")
        beep_test_laps = data.get("beep_test_laps")
        max_hr = data.get("max_hr")
        if beep_test_level is None or beep_test_laps is None:
            return api.create_response(
                request, {"detail": "beep_test_level and beep_test_laps are required"}, status=422
            )
        beep_test_total_laps = calculate_beep_test_total_laps(beep_test_level, beep_test_laps)
        beep_test_score = calculate_score(
            profile.age,
            profile.gender,
            "beep_test",
            beep_test_total_laps
        )
        if beep_test_score is None:
            return api.create_response(
                request,
                {"detail": "Invalid beep test values - check input data"},
                status=422
            )
        test_result, created = TestResult.objects.update_or_create(
            profile=profile,
            active_test=active_test,
            defaults={
                "beep_test_level": beep_test_level,
                "beep_test_laps": beep_test_laps,
                "beep_test_total_laps": beep_test_total_laps,
                "max_hr": max_hr,
                "beep_test_score": beep_test_score,
                "test_name": active_test.name,
                "test_date": date.today(),
                "team": active_test.team,
            }
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["profile_id"] = test_result.profile.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/recalculate-scores")
def recalculate_scores_api(request):
    """Recalculate all scores for the current user's teams (or all if superuser)"""
    from .recalculate_scores import recalculate_scores
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # request.auth is the username string from AuthBearer
    user = User.objects.get(username=request.auth)
    recalculate_scores(user)
    return {"success": True, "message": "Scores recalculated successfully."}

@api.get("/results/profile/{profile_id}/active-test/{active_test_id}", response=TestResultSchema)
def get_profile_active_test_result(request, profile_id: int, active_test_id: int):
    """Get the latest test result for a specific profile and active test"""
    try:
        result = TestResult.objects.filter(
            profile_id=profile_id,
            active_test_id=active_test_id
        ).order_by('-test_date').first()
        
        if not result:
            return api.create_response(
                request,
                {"detail": "No test result found for this profile and active test"},
                status=404
            )
            
        from django.forms.models import model_to_dict
        response_data = model_to_dict(result)
        response_data["team"] = result.team.name if result.team else None
        response_data["profile_id"] = result.profile.id
        response_data["test_date"] = result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.get("/results/profile/{profile_id}/test-type/{test_type}", response=TestResultSchema)
def get_latest_profile_test_type_result(request, profile_id: int, test_type: str):
    """Get the latest test result for a specific profile and test type"""
    field_name = f"{test_type}_score"
    result = (
        TestResult.objects.filter(profile_id=profile_id)
        .exclude(**{field_name: None})
        .order_by("-test_date")
        .first()
    )
    if not result:
        return api.create_response(
            request,
            {"detail": "No test result found for this profile and test type"},
            status=404
        )
    from django.forms.models import model_to_dict
    response_data = model_to_dict(result)
    response_data["team"] = result.team.name if result.team else None
    response_data["profile_id"] = result.profile.id
    response_data["test_date"] = result.test_date
    return response_data
