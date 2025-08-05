from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TestResult
from .models import Person
from .models import Event
from .models import Team
from .models import PersonMeasurement


@admin.register(TestResult)
@admin.register(Person)
@admin.register(Event)
@admin.register(Team)
@admin.register(PersonMeasurement)
class CustomAdminClass(ModelAdmin):
    pass
