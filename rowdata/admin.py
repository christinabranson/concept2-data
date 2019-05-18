from django.contrib import admin

# Register your models here.
from . import models

class WorkoutsInLine(admin.TabularInline):
    model = models.Workout
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "_workouts")

    search_fields = ["email", "first_name", "last_name"]

    inlines = [
        WorkoutsInLine
    ]

    list_per_page = 25

    def _workouts(self, obj):
        return obj.workouts.all().count()

admin.site.register(models.User, UserAdmin)