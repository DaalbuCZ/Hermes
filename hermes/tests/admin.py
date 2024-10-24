from django.contrib import admin
from .models import TestResult
from .models import Profile

admin.site.register(TestResult)
admin.site.register(Profile)
