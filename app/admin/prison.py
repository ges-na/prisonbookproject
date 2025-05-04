from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from app.models.prison import Prison


class PrisonResource(resources.ModelResource):
    class Meta:
        model = Prison
        skip_unchanged = True
        report_skipped = True
        fields = (
            "id",
            "name",
            "prison_type",
            "legacy_id",
            "legacy_address",
            "mailing_address",
            "additional_mailing_headers",
            "mailing_city",
            "mailing_state",
            "mailing_zipcode",
            "restrictions",
            "notes",
        )


class PrisonAdmin(ImportExportModelAdmin):
    resource_class = PrisonResource

    list_display = (
        "id",
        "name",
        "prison_type",
        "display_mailing_address",
        "restrictions",
        "notes",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
    )
    list_display_links = ("name",)
    list_filter = ("prison_type",)
    search_fields = (
        "name",
        "notes",
        "restrictions",
    )
    fields = (
        "name",
        "prison_type",
        "additional_mailing_headers",
        "mailing_address",
        "mailing_city",
        "mailing_state",
        "mailing_zipcode",
        "legacy_address",
        "restrictions",
        "notes",
    )

    def display_mailing_address(self, prison):
        if not prison.mailing_address:
            return
        if prison.additional_mailing_headers:
            return format_html(
                f"{prison.name}<br/>{prison.additional_mailing_headers}<br/>{prison.mailing_address}<br/>{prison.mailing_city}, {prison.mailing_state} {prison.mailing_zipcode}"
            )
        return format_html(
            f"{prison.name}<br/>{prison.mailing_address}<br/>{prison.mailing_city}, {prison.mailing_state} {prison.mailing_zipcode}"
        )

    display_mailing_address.allow_tags = True
    display_mailing_address.short_description = "Mailing Address"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
