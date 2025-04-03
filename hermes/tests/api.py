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
    id: int
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
    agility_score: float | None
    endurance_score: float | None
    speed_score: float | None
    strength_score: float | None


class TeamSchema(Schema):
    id: int
    name: str
    created_at: date


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
