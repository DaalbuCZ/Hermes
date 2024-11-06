from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TestResultDatabase


@admin.register(TestResultDatabase)
class TestResultDatabaseAdmin(ModelAdmin):
    list_display = ("name", "created_at")
