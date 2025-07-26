from ninja import NinjaAPI, Schema, Body  # Add this import
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from .models import Person, TestResult, Event, Team, PersonMeasurement
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
class PersonSchema(Schema):
    id: int | None = None  # Make id optional for creation
    name: str
    surname: str
    date_of_birth: date
    gender: str
    height: float
    weight: float
    team_id: int | None = None  # Optional for input
    age: int | None = None      # Optional for input


class TestResultSchema(Schema):
    id: int
    person_id: int
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
    beep_test_number: int | None
    max_hr: int | None


class TeamSchema(Schema):
    id: int
    name: str
    created_at: datetime


# Additional schemas
class EventSchema(Schema):
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


class PersonMeasurementSchema(Schema):
    id: int | None = None
    person_id: int
    measurement_date: date
    height: float
    weight: float
    notes: str | None = None
    recorded_by_id: int | None = None
    created_at: datetime | None = None


class PersonMeasurementCreateSchema(Schema):
    measurement_date: date
    height: float
    weight: float
    notes: str | None = None


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
@api.get("/people", response=List[PersonSchema])
def get_people(request):
    # Return each person as a dict with age
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
        for p in Person.objects.all()
    ]


@api.get("/person/{person_id}", response=PersonSchema)
def get_person(request, person_id: int):
    return get_object_or_404(Person, id=person_id)


@api.get("/results", response=List[TestResultSchema])
def get_test_results(request):
    results = TestResult.objects.all()
    # Serialize team as string (team name) for each result
    serialized = []
    for r in results:
        d = r.__dict__.copy()
        d["team"] = r.team.name if hasattr(r, "team") and r.team else None
        d["person_id"] = r.person.id if hasattr(r, "person") and r.person else None
        d["test_date"] = r.test_date
        serialized.append(d)
    return serialized


@api.get("/results/{person_id}", response=List[TestResultSchema])
def get_person_results(request, person_id: int):
    return TestResult.objects.filter(person_id=person_id)


@api.get("/teams", response=List[TeamSchema])
def get_teams(request):
    if not request.auth or not request.auth.is_superuser:
        return api.create_response(request, {"detail": "Not authorized"}, status=403)
    return Team.objects.all()


@api.get("/team/{team_id}/results", response=List[TestResultSchema])
def get_team_results(request, team_id: int):
    return TestResult.objects.filter(person__team_id=team_id)


# Person endpoints
@api.post("/people", response=PersonSchema)
def create_person(request, person: PersonSchema):
    person_data = person.dict(exclude={"id", "age", "team_id"})  # Exclude id, age, team_id from input
    # Set team_id from the authenticated user if available
    team_id = None
    if hasattr(request.auth, "teams") and request.auth.teams.exists():
        team_id = request.auth.teams.first().id
    person_data["team_id"] = team_id
    new_person = Person.objects.create(**person_data)
    # Find the active test for the new person's team
    event = Event.objects.filter(is_active=True, team=new_person.team).first()
    # Create a blank TestResult for the new person, with the active test if available
    TestResult.objects.create(person=new_person, team=new_person.team, event=event)
    return new_person


@api.put("/person/{person_id}", response=PersonSchema)
def update_person(request, person_id: int, person: PersonSchema):
    person_obj = get_object_or_404(Person, id=person_id)
    for key, value in person.dict(exclude_unset=True).items():
        setattr(person_obj, key, value)
    person_obj.save()
    return person_obj


@api.delete("/person/{person_id}")
def delete_person(request, person_id: int):
    person = get_object_or_404(Person, id=person_id)
    person.delete()
    return {"success": True}


# Test result endpoints
@api.post("/results", response=TestResultSchema)
def create_test_result(request, test_result: TestResultSchema):
    person = get_object_or_404(Person, id=test_result.person_id)
    return TestResult.objects.create(
        person=person, **test_result.dict(exclude={"person_id"})
    )


@api.put("/results/{result_id}", response=TestResultSchema)
def update_test_result(request, result_id: int, test_result: TestResultSchema):
    result = get_object_or_404(TestResult, id=result_id)
    for key, value in test_result.dict(
        exclude_unset=True, exclude={"person_id"}
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
@api.get("/results/latest/{person_id}", response=TestResultSchema)
def get_latest_person_result(request, person_id: int):
    return (
        TestResult.objects.filter(person_id=person_id).order_by("-test_date").first()
    )


@api.get("/results/team/{team_id}/latest", response=List[TestResultSchema])
def get_team_latest_results(request, team_id: int):
    return (
        TestResult.objects.filter(person__team_id=team_id)
        .order_by("person_id", "-test_date")
        .distinct("person_id")
    )


@api.get("/results/aggregate/{person_id}")
def get_person_aggregate_scores(request, person_id: int):
    latest_result = (
        TestResult.objects.filter(person_id=person_id).order_by("-test_date").first()
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
@api.get("/events", response=List[EventSchema])
def get_events(request):
    """Get all active tests, filtered by user's teams if not superuser"""
    if request.auth.is_superuser:
        return Event.objects.all()
    return Event.objects.filter(team__in=request.auth.teams.all())


@api.get("/events/{team_id}", response=List[EventSchema])
def get_team_active_tests(request, team_id: int):
    """Get active tests for a specific team"""
    return Event.objects.filter(team_id=team_id, is_active=True)


@api.post("/events", response=EventSchema)
def create_event(request, event: EventSchema):
    """Create a new active test"""
    # Deactivate all other tests for the team if this one is active
    if event.is_active and event.team_id:
        Event.objects.filter(team_id=event.team_id, is_active=True).update(
            is_active=False
        )
    return Event.objects.create(**event.dict())


@api.put("/events/{event_id}", response=EventSchema)
def update_event(request, event_id: int, event: EventSchema):
    """Update an active test"""
    event_obj = get_object_or_404(Event, id=event_id)
    if event.is_active and event.team_id:
        # Deactivate other tests only if we're activating this one
        if not event_obj.is_active:
            Event.objects.filter(
                team_id=event.team_id, is_active=True
            ).update(is_active=False)
    for key, value in event.dict(exclude_unset=True).items():
        setattr(event_obj, key, value)
    event_obj.save()
    return event_obj


@api.delete("/events/{event_id}")
def delete_event(request, event_id: int):
    """Delete an active test"""
    event = get_object_or_404(Event, id=event_id)
    event.delete()
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
    return TestResult.objects.filter(person__team_id=team_id).exclude(
        **{field_name: None}
    )


@api.get(
    "/results/test-type/{test_type}/person/{person_id}",
    response=List[TestResultSchema],
)
def get_person_results_by_test_type(request, test_type: str, person_id: int):
    """Get profile results filtered by test type"""
    field_name = f"{test_type}_score"
    return TestResult.objects.filter(person_id=person_id).exclude(
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
        results = TestResult.objects.filter(person__team_id=team_id).exclude(
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
        results = TestResult.objects.filter(person__team_id=team_id).exclude(
            **{field_name: None}
        )
        stats[f"{score_type}_composite"] = {
            "avg_score": results.aggregate(Avg(field_name))[f"{field_name}__avg"],
            "max_score": results.aggregate(Max(field_name))[f"{field_name}__max"],
            "min_score": results.aggregate(Min(field_name))[f"{field_name}__min"],
        }

    return stats


@api.get("/statistics/person/{person_id}")
def get_person_progress(request, person_id: int):
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
            TestResult.objects.filter(person_id=person_id)
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
@api.post("/ladder-test/{person_id}", response=TestResultSchema)
def save_ladder_test(request, person_id: int, data: dict = Body(...)):
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

        person = get_object_or_404(Person, id=person_id)
        # print(f"Profile found - ID: {profile.id}, Age: {profile.age}, Gender: {profile.gender}, Team: {profile.team}")
        event = Event.objects.filter(is_active=True, team=person.team).first()
        # print(f"Active test found: {active_test is not None}")

        if not event:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )

        score = calculate_score(
            person.age,
            person.gender,
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

        test_result = get_or_create_test_result(
            person,
            event,
            ladder_time_1=data.get("ladder_time_1"),
            ladder_time_2=data.get("ladder_time_2"),
            ladder_score=score,
            test_name=event.name,
            test_date=date.today(),
            team=event.team,
        )

        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["person_id"] = test_result.person.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        # print(f"Error processing ladder test: {str(e)}")
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/brace-test/{person_id}", response=TestResultSchema)
def save_brace_test(request, person_id: int, data: dict = Body(...)):
    person = get_object_or_404(Person, id=person_id)
    event = Event.objects.filter(is_active=True, team=person.team).first()
    
    if not event:
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

    test_result = get_or_create_test_result(
        person,
        event,
        brace_time_1=data.get("brace_time_1"),
        brace_time_2=data.get("brace_time_2"),
        brace_score=calculate_score(
            person.age,
            person.gender,
            "brace",
            data.get("brace_time_1"),
            data.get("brace_time_2")
        ),
        test_name=event.name,
        test_date=date.today(),
        team=event.team,
    )
    test_result.save()
    from django.forms.models import model_to_dict
    response_data = model_to_dict(test_result)
    response_data["team"] = test_result.team.name if test_result.team else None
    response_data["person_id"] = test_result.person.id
    response_data["test_date"] = test_result.test_date
    return response_data

@api.post("/hexagon-test/{person_id}", response=TestResultSchema)
def save_hexagon_test(request, person_id: int, data: dict = Body(...)):
    try:
        if (
            (data.get("hexagon_time_cw") is not None and not isinstance(data.get("hexagon_time_cw"), (int, float)))
            or
            (data.get("hexagon_time_ccw") is not None and not isinstance(data.get("hexagon_time_ccw"), (int, float)))
        ):
            return api.create_response(
                request, {"detail": "Invalid times - each time must be a number or null"}, status=422
            )
        person = get_object_or_404(Person, id=person_id)
        event = Event.objects.filter(is_active=True, team=person.team).first()
        if not event:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        score = calculate_score(
            person.age,
            person.gender,
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
        test_result = get_or_create_test_result(
            person,
            event,
            hexagon_time_cw=data.get("hexagon_time_cw"),
            hexagon_time_ccw=data.get("hexagon_time_ccw"),
            hexagon_score=score,
            test_name=event.name,
            test_date=date.today(),
            team=event.team,
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["person_id"] = test_result.person.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/y-test/{person_id}", response=TestResultSchema)
def save_y_test(request, person_id: int, data: dict = Body(...)):
    try:
        person = get_object_or_404(Person, id=person_id)
        event = Event.objects.filter(is_active=True, team=person.team).first()
        if not event:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        y_test_score = calculate_score(
            person.age,
            person.gender,
            "y_test",
            person.height,
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
            person.height,
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
        test_result = get_or_create_test_result(
            person,
            event,
            y_test_ll_front=data.get("y_test_ll_front"),
            y_test_ll_left=data.get("y_test_ll_left"),
            y_test_ll_right=data.get("y_test_ll_right"),
            y_test_rl_front=data.get("y_test_rl_front"),
            y_test_rl_left=data.get("y_test_rl_left"),
            y_test_rl_right=data.get("y_test_rl_right"),
            y_test_la_left=data.get("y_test_la_left"),
            y_test_la_front=data.get("y_test_la_front"),
            y_test_la_back=data.get("y_test_la_back"),
            y_test_ra_right=data.get("y_test_ra_right"),
            y_test_ra_front=data.get("y_test_ra_front"),
            y_test_ra_back=data.get("y_test_ra_back"),
            y_test_score=y_test_score,
            y_test_index=y_test_index,
            test_name=event.name,
            test_date=date.today(),
            team=event.team,
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["person_id"] = test_result.person.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/medicimbal-test/{person_id}", response=TestResultSchema)
def save_medicimbal_test(request, person_id: int, data: dict = Body(...)):
    try:
        for i in [1, 2, 3]:
            val = data.get(f"medicimbal_throw_{i}")
            if val is not None and not isinstance(val, (int, float)):
                return api.create_response(
                    request, {"detail": f"Throw {i} must be a number or null"}, status=422
                )
        person = get_object_or_404(Person, id=person_id)
        event = Event.objects.filter(is_active=True, team=person.team).first()
        if not event:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        score = calculate_score(
            person.age,
            person.gender,
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
        test_result = get_or_create_test_result(
            person,
            event,
            medicimbal_throw_1=data.get("medicimbal_throw_1"),
            medicimbal_throw_2=data.get("medicimbal_throw_2"),
            medicimbal_throw_3=data.get("medicimbal_throw_3"),
            medicimbal_score=score,
            test_name=event.name,
            test_date=date.today(),
            team=event.team,
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["person_id"] = test_result.person.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/jet-test/{person_id}", response=TestResultSchema)
def save_jet_test(request, person_id: int, data: dict = Body(...)):
    try:
        person = get_object_or_404(Person, id=person_id)
        event = Event.objects.filter(is_active=True, team=person.team).first()
        if not event:
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
            person.age,
            person.gender,
            "jet",
            jet_distance
        )
        if score is None:
            return api.create_response(
                request,
                {"detail": "Invalid jet test values - check input data"},
                status=422
            )
        test_result = get_or_create_test_result(
            person,
            event,
            jet_laps=jet_laps,
            jet_sides=jet_sides,
            jet_distance=jet_distance,
            jet_score=score,
            test_name=event.name,
            test_date=date.today(),
            team=event.team,
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["person_id"] = test_result.person.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.post("/triple-jump-test/{person_id}", response=TestResultSchema)
def save_triple_jump_test(request, person_id: int, data: dict = Body(...)):
    try:
        for i in [1, 2, 3]:
            val = data.get(f"triple_jump_distance_{i}")
            if val is not None and not isinstance(val, (int, float)):
                return api.create_response(
                    request, {"detail": f"Jump distance {i} must be a number or null"}, status=422
                )
        person = get_object_or_404(Person, id=person_id)
        event = Event.objects.filter(is_active=True, team=person.team).first()
        if not event:
            return api.create_response(
                request, {"detail": "No active test found for this profile's team"}, status=400
            )
        score = calculate_score(
            person.age,
            person.gender,
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
        test_result = get_or_create_test_result(
            person,
            event,
            triple_jump_distance_1=data.get("triple_jump_distance_1"),
            triple_jump_distance_2=data.get("triple_jump_distance_2"),
            triple_jump_distance_3=data.get("triple_jump_distance_3"),
            triple_jump_score=score,
            test_name=event.name,
            test_date=date.today(),
            team=event.team,
        )
        test_result.save()
        from django.forms.models import model_to_dict
        response_data = model_to_dict(test_result)
        response_data["team"] = test_result.team.name if test_result.team else None
        response_data["person_id"] = test_result.person.id
        response_data["test_date"] = test_result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

class BeepTestBatchItem(Schema):
    person_id: int
    beep_test_level: int
    beep_test_laps: int
    beep_test_number: Optional[int] = None
    max_hr: Optional[int] = None

class BeepTestBatchResponse(Schema):
    person_id: int
    success: bool
    result: Optional[TestResultSchema] = None
    error: Optional[str] = None

@api.post("/beep-test/batch", response=List[BeepTestBatchResponse])
def save_beep_test_batch(request, items: List[BeepTestBatchItem]):
    responses = []
    for item in items:
        try:
            person = get_object_or_404(Person, id=item.person_id)
            event = Event.objects.filter(is_active=True, team=person.team).first()
            if not event:
                responses.append(BeepTestBatchResponse(
                    person_id=item.person_id,
                    success=False,
                    error="No active test found for this profile's team"
                ))
                continue
            beep_test_total_laps = calculate_beep_test_total_laps(item.beep_test_level, item.beep_test_laps)
            beep_test_score = calculate_score(
                person.age,
                person.gender,
                "beep_test",
                beep_test_total_laps
            )
            if beep_test_score is None:
                responses.append(BeepTestBatchResponse(
                    person_id=item.person_id,
                    success=False,
                    error="Invalid beep test values - check input data"
                ))
                continue
            test_result = get_or_create_test_result(
                person,
                event,
                beep_test_level=item.beep_test_level,
                beep_test_laps=item.beep_test_laps,
                beep_test_total_laps=beep_test_total_laps,
                beep_test_number=item.beep_test_number,
                max_hr=item.max_hr,
                beep_test_score=beep_test_score,
                test_name=event.name,
                test_date=date.today(),
                team=event.team,
            )
            test_result.save()
            from django.forms.models import model_to_dict
            response_data = model_to_dict(test_result)
            response_data["team"] = test_result.team.name if test_result.team else None
            response_data["person_id"] = test_result.person.id
            response_data["test_date"] = test_result.test_date
            responses.append(BeepTestBatchResponse(
                person_id=item.person_id,
                success=True,
                result=response_data
            ))
        except Exception as e:
            responses.append(BeepTestBatchResponse(
                person_id=item.person_id,
                success=False,
                error=str(e)
            ))
    return responses

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

@api.get("/results/person/{person_id}/event/{event_id}", response=TestResultSchema)
def get_person_event_result(request, person_id: int, event_id: int):
    """Get the latest test result for a specific profile and event"""
    try:
        result = TestResult.objects.filter(
            person_id=person_id,
            event_id=event_id
        ).order_by('-test_date').first()
        
        if not result:
            return api.create_response(
                request,
                {"detail": "No test result found for this profile and event"},
                status=404
            )
            
        from django.forms.models import model_to_dict
        response_data = model_to_dict(result)
        response_data["team"] = result.team.name if result.team else None
        response_data["person_id"] = result.person.id
        response_data["test_date"] = result.test_date
        return response_data
    except Exception as e:
        return api.create_response(
            request,
            {"detail": str(e)},
            status=422
        )

@api.get("/results/person/{person_id}/test-type/{test_type}", response=TestResultSchema)
def get_latest_person_test_type_result(request, person_id: int, test_type: str):
    """Get the latest test result for a specific profile and test type"""
    field_name = f"{test_type}_score"
    result = (
        TestResult.objects.filter(person_id=person_id)
        .exclude(**{field_name: None})
        .order_by("-test_date")
        .first()
    )
    if not result:
        return None  # Return 200 with null
    from django.forms.models import model_to_dict
    response_data = model_to_dict(result)
    response_data["team"] = result.team.name if result.team else None
    response_data["person_id"] = result.person.id
    response_data["test_date"] = result.test_date
    return response_data

class ProfileIdsSchema(Schema):
    profile_ids: list[int]

@api.post("/beep-test/has-results", response=dict)
def beep_test_has_results(request, data: ProfileIdsSchema):
    result = {}
    for pid in data.profile_ids:
        has_result = TestResult.objects.filter(
            person_id=pid
        ).exclude(beep_test_score=None).exists()
        result[pid] = has_result
    return result

@api.post("/beep-test/batch-latest", response=Dict[int, TestResultSchema | None])
def beep_test_batch_latest(request, data: ProfileIdsSchema):
    result = {}
    for pid in data.profile_ids:
        field_name = "beep_test_score"
        latest = (
            TestResult.objects.filter(person_id=pid)
            .exclude(**{field_name: None})
            .order_by("-test_date")
            .first()
        )
        if latest:
            from django.forms.models import model_to_dict
            response_data = model_to_dict(latest)
            response_data["team"] = latest.team.name if latest.team else None
            response_data["person_id"] = latest.person.id
            response_data["test_date"] = latest.test_date
            result[pid] = response_data
        else:
            result[pid] = None
    return result

def get_or_create_test_result(person, event=None, **kwargs):
    filters = {'person': person}
    if event is not None:
        filters['event'] = event
    test_result, created = TestResult.objects.get_or_create(
        **filters,
        defaults=kwargs,
    )
    if not created:
        for key, value in kwargs.items():
            setattr(test_result, key, value)
    return test_result


# Measurement endpoints
@api.get("/persons/{person_id}/measurements", response=List[PersonMeasurementSchema])
def get_person_measurements(request, person_id: int):
    """Get measurement history for a person"""
    person = get_object_or_404(Person, id=person_id)
    measurements = person.get_measurement_history()
    
    return [
        {
            "id": m.id,
            "person_id": m.person.id,
            "measurement_date": m.measurement_date,
            "height": m.height,
            "weight": m.weight,
            "notes": m.notes,
            "recorded_by_id": m.recorded_by.id if m.recorded_by else None,
            "created_at": m.created_at,
        }
        for m in measurements
    ]


@api.get("/persons/{person_id}/measurements/latest", response=PersonMeasurementSchema)
def get_latest_person_measurement(request, person_id: int):
    """Get the latest measurement for a person"""
    person = get_object_or_404(Person, id=person_id)
    measurement = person.get_latest_measurement()
    
    if not measurement:
        return api.create_response(
            request,
            {"detail": "No measurements found for this person"},
            status=404
        )
    
    return {
        "id": measurement.id,
        "person_id": measurement.person.id,
        "measurement_date": measurement.measurement_date,
        "height": measurement.height,
        "weight": measurement.weight,
        "notes": measurement.notes,
        "recorded_by_id": measurement.recorded_by.id if measurement.recorded_by else None,
        "created_at": measurement.created_at,
    }


@api.post("/persons/{person_id}/measurements", response=PersonMeasurementSchema)
def add_person_measurement(request, person_id: int, measurement: PersonMeasurementCreateSchema):
    """Add a new measurement for a person"""
    person = get_object_or_404(Person, id=person_id)
    
    # Check if measurement for this date already exists
    existing_measurement = PersonMeasurement.objects.filter(
        person=person,
        measurement_date=measurement.measurement_date
    ).first()
    
    if existing_measurement:
        return api.create_response(
            request,
            {"detail": "Measurement for this date already exists"},
            status=400
        )
    
    # Create new measurement
    new_measurement = PersonMeasurement.objects.create(
        person=person,
        measurement_date=measurement.measurement_date,
        height=measurement.height,
        weight=measurement.weight,
        notes=measurement.notes,
        recorded_by=request.auth,
    )
    
    return {
        "id": new_measurement.id,
        "person_id": new_measurement.person.id,
        "measurement_date": new_measurement.measurement_date,
        "height": new_measurement.height,
        "weight": new_measurement.weight,
        "notes": new_measurement.notes,
        "recorded_by_id": new_measurement.recorded_by.id if new_measurement.recorded_by else None,
        "created_at": new_measurement.created_at,
    }


@api.put("/persons/{person_id}/measurements/{measurement_id}", response=PersonMeasurementSchema)
def update_person_measurement(request, person_id: int, measurement_id: int, measurement: PersonMeasurementCreateSchema):
    """Update an existing measurement"""
    person = get_object_or_404(Person, id=person_id)
    existing_measurement = get_object_or_404(PersonMeasurement, id=measurement_id, person=person)
    
    # Update fields
    existing_measurement.measurement_date = measurement.measurement_date
    existing_measurement.height = measurement.height
    existing_measurement.weight = measurement.weight
    existing_measurement.notes = measurement.notes
    existing_measurement.save()
    
    return {
        "id": existing_measurement.id,
        "person_id": existing_measurement.person.id,
        "measurement_date": existing_measurement.measurement_date,
        "height": existing_measurement.height,
        "weight": existing_measurement.weight,
        "notes": existing_measurement.notes,
        "recorded_by_id": existing_measurement.recorded_by.id if existing_measurement.recorded_by else None,
        "created_at": existing_measurement.created_at,
    }


@api.delete("/persons/{person_id}/measurements/{measurement_id}")
def delete_person_measurement(request, person_id: int, measurement_id: int):
    """Delete a measurement"""
    person = get_object_or_404(Person, id=person_id)
    measurement = get_object_or_404(PersonMeasurement, id=measurement_id, person=person)
    measurement.delete()
    return {"success": True}
