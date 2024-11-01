from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TestResult
from .models import Profile


@admin.register(TestResult)
@admin.register(Profile)
class CustomAdminClass(ModelAdmin):
    pass
