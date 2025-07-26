from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TestResult
from .models import Person


@admin.register(TestResult)
@admin.register(Person)
class CustomAdminClass(ModelAdmin):
    pass
