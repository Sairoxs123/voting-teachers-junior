from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Contestants)

class ContestantsAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'name', 'position', 'votes']
    search_fields = ['name', 'position']
    list_filter = ['position']


@admin.register(Votes)

class VotesAdmin(admin.ModelAdmin):
    ordering = ["id"]
    list_display = ["id", "contestant", "email"]


@admin.register(History)

class HistoryAdmin(admin.ModelAdmin):
    ordering = ["id"]
    list_display = ["id", "email", "contestant_name", "position", "date"]
    list_filter = ["date"]
