from datetime import datetime

from django.contrib import admin

from src.app.models.problem_note import ProblemNote


class ProblemNoteAdmin(admin.ModelAdmin):
    def last_updated_date(self, note: ProblemNote):
        return note.modified_date if note.modified_date else note.created_date

    def last_updated_by(self, note: ProblemNote):
        return note.modified_by if note.modified_by else note.created_by

    list_display = ("note", "person", "letter", "last_updated_by", "last_updated_date")
    readonly_fields = (
        "person",
        "letter",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
    )
    list_display_links = ("note",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.modified_date = datetime.now()
        super().save_model(request, obj, form, change)
