from django.contrib import admin
from django.forms import ModelForm, ValidationError, fields
from django.urls import reverse
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from src.app.models.person import Person
from src.app.models.prison import PersonPrison, Prison
from src.app.utils import NO_PRISON_STR, WorkflowStage


class PersonResource(resources.ModelResource):
    current_prison = Field(attribute="current_prison")
    last_served = Field(attribute="last_served")
    eligible = Field(attribute="eligible")
    package_count = Field(attribute="package_count")
    letter_count = Field(attribute="letter_count")

    class Meta:
        model = Person
        skip_unchanged = True
        report_skipped = True
        fields = (
            "id",
            "inmate_number",
            "last_name",
            "middle_name",
            "first_name",
            "name_suffix",
            "status",
        )
        readonly_fields = (
            "current_prison",
            "last_served",
            "get_eligibility_str",
            "letter_count",
            "package_count",
        )
        export_order = (
            "id",
            "last_name",
            "middle_name",
            "first_name",
            "name_suffix",
            "status",
            "current_prison",
            "last_served",
            "eligible",
            "letter_count",
            "package_count",
        )

class PersonAdminForm(ModelForm):
    allow_empty_inmate = False

    class Meta:
        model = Person
        fields = [
            "inmate_number",
            "last_name",
            "middle_name",
            "first_name",
            "name_suffix",
            "status",
            "notes",
        ]

    def clean_inmate_number(self):
        inmate_number = self.cleaned_data.get("inmate_number", "")
        if not self.allow_empty_inmate and not inmate_number:
            raise ValidationError("Inmate ID is required")
        inmate_number = "".join(list(filter(str.isalnum, inmate_number)))
        return inmate_number.upper()

    def clean_first_name(self):
        return self.cleaned_data["first_name"].upper()

    def clean_middle_name(self):
        return self.cleaned_data["middle_name"].upper()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].upper()

    def clean_name_suffix(self):
        return self.cleaned_data["name_suffix"].upper()


class PersonCreateForm(PersonAdminForm):
    inmate_number = fields.CharField(required=False)
    did_not_include_inmate_number = fields.BooleanField(initial=False, required=False)

    allow_empty_inmate = True

    class Meta(PersonAdminForm.Meta):
        fields = [
            "inmate_number",
            "did_not_include_inmate_number",
            "last_name",
            "middle_name",
            "first_name",
            "name_suffix",
            "status",
            "notes",
        ]

    def clean(self):
        cleaned_data = super().clean()
        assert cleaned_data  # make pyright happy
        inmate_number = cleaned_data.get("inmate_number", "")
        did_not = cleaned_data.get("did_not_include_inmate_number", False)
        if not inmate_number and not did_not:
            raise ValidationError(
                "No inmate number included. If one was not provided, leave blank but also check 'Did Not Include Inmate Number'"
            )
        elif inmate_number and did_not:
            raise ValidationError(
                "Inmate ID must be blank if 'Did Not Include Inmate Number' is checked"
            )
        elif did_not:
            if not (last_person := Person.objects.all().order_by("pk").last()):
                last_pk = 0
            else:
                last_pk = last_person.pk
            cleaned_data["inmate_number"] = f"UNKNOWNID{last_pk}"
        return cleaned_data


class PersonPrisonInline(admin.TabularInline):
    model = PersonPrison
    max_num = 1
    verbose_name = "Prison"
    verbose_name_plural = "Prisons"
    fields = ("prison",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "prison":
            kwargs["queryset"] = Prison.objects.all().order_by("name")
            kwargs["empty_label"] = NO_PRISON_STR
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Override the formset function in order to remove the add and
        change buttons beside the foreign key pull-down menus in the inline.
        From: https://stackoverflow.com/a/37558444
        """
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields["prison"].widget
        widget.can_add_related = False
        widget.can_change_related = False
        return formset


class PersonAdmin(ImportExportModelAdmin):
    resource_class = PersonResource

    def last_served_date(self, obj) -> str | None:
        if obj.last_served:
            return obj.last_served.strftime("%Y-%m-%d")

    list_display = (
        "inmate_number",
        "last_name",
        "first_name",
        "get_eligibility_str",
        "status",
        "last_served_date",
        "current_prison",
        "package_count",
        "pending_letter_count",
        "letter_count",
        "created_by",
        "created_date",
        "modified_date",
    )
    readonly_fields = (
        "current_prison",
        "created_by",
        "created_date",
        "modified_date",
        "get_eligibility_str",
        "package_count",
        "pending_letter_count",
        "letter_count",
    )
    list_filter = (
        # "prisons__prison",
        # EligibilityListFilter,
    )
    search_fields = (
        "inmate_number",
        "last_name",
        "first_name",
    )
    list_display_links = (
        "first_name",
        "last_name",
    )
    list_per_page = 25
    inlines = [PersonPrisonInline]

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            return PersonCreateForm
        return PersonAdminForm

    def get_fields(self, request, obj=None):
        if obj:
            return PersonAdminForm.Meta.fields
        else:
            return PersonCreateForm.Meta.fields

    def current_prison(self, person) -> str:
        if not person.current_prison:
            return NO_PRISON_STR
        link = reverse(
            "admin:app_prison_change", kwargs={"object_id": person.current_prison.id}
        )
        return format_html("<a href={}>{}</a>", link, person.current_prison.name)

    def pending_letter_count(self, person):
        if not person.pending_letter_count:
            return
        return format_html(
            "<a href={}?person={}&workflow_stage={} target='_blank'>{}</a>",
            reverse("admin:app_letter_changelist"),
            person.id,
            WorkflowStage.STAGE1_COMPLETE,
            person.pending_letter_count,
        )

    def letter_count(self, person):
        if not person.letter_count:
            return
        return format_html(
            "<a href={}?person={}>{}</a>",
            reverse("admin:app_letter_changelist"),
            person.id,
            person.letter_count,
        )

    def package_count(self, person):
        if not person.package_count:
            return
        return format_html(
            "<a href={}?person={}&workflow_stage__in={}>{}</a>",
            reverse("admin:app_letter_changelist"),
            person.id,
            WorkflowStage.FULFILLED,
            person.package_count,
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
