from __future__ import annotations

from functools import wraps
from typing import Callable, Literal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView as DjLoginView,
    PasswordResetView as DjPasswordResetView,
)
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django_registration.backends.activation.views import RegistrationView as Dj_Reg

from src.app.forms import (
    AuthenticationForm,
    ContribLetterForm,
    ContribLetterIssueForm,
    ContribPersonForm,
    ContribPersonIssueForm,
    PasswordResetForm,
    RegistrationForm,
)
from src.app.models.letter import Letter
from src.app.models.person import Person


def check_auth(func: Callable) -> Callable:
    """
    No user / user not logged in: redirect to login
    Non-contrib, non-staff user: send to non_contributor page
    """

    @wraps(func)
    def wrapper(request):
        # not authenticated; log in
        if not request.user or not request.user.is_authenticated:
            return redirect("/accounts/login")
        # not a contributor or staff, needs permission
        elif not request.user.is_contributor and not request.user.is_staff:
            return redirect("/contrib/not_contributor")
        return func(request)

    return wrapper


def redirect_to_admin(request):
    """
    Redirect base URL to admin site.
    """
    return HttpResponseRedirect("/admin")


def not_contributor(request):
    return render(request, "contributors/not_contributor.html")


def contrib_logout(request):
    return render(request, "contributors/logout.html")


@check_auth
def contrib_letter_form(request):
    if request.method == "POST":
        form = ContribLetterForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Letter created.")
            return redirect("contrib_letter_add")
    else:
        form = ContribLetterForm(request.user)
    return render(request, "contributors/add_letter.html", {"form": form})


@check_auth
def contrib_person_form(request):
    if request.method == "POST":
        form = ContribPersonForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Person created.")
            return redirect("contrib_person_add")
    else:
        form = ContribPersonForm(request.user)
    return render(request, "contributors/add_person.html", {"form": form})


@check_auth
def contrib_letter_issue_form(request):
    return contrib_issue_form_base(request, ContribLetterIssueForm, Letter, "letter")


@check_auth
def contrib_person_issue_form(request):
    return contrib_issue_form_base(request, ContribPersonIssueForm, Person, "person")


def contrib_issue_form_base(
    request,
    form_class: type[ContribPersonIssueForm] | type[ContribLetterIssueForm],
    model: type[Letter] | type[Person],
    form_type: Literal["person"] | Literal["letter"],
):
    record_id = request.GET.get(form_type)
    initial = get_initial_issue_form_data(form_type, record_id, model)
    if request.method == "POST":
        form = form_class(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Issue added.")
            return redirect("contrib_profile")
    else:
        record = model.objects.get(id=record_id)
        if not record.created_by == request.user:
            messages.error(
                request,
                f"You do not have permission to add an issue for this {form_type}.",
            )
            return redirect("contrib_profile")
        form = form_class(request.user, initial=initial)
    return render(
        request,
        "contributors/add_issue.html",
        {"form_type": form_type, "form": form, "record_id": record_id},
    )


def get_initial_issue_form_data(form_type, record_id, model):
    record = model.objects.get(id=record_id)
    return {form_type: record}


def get_blank_form_with_context(form_type, model, record_id, form_class, request):
    initial = {}
    record = model.objects.get(id=record_id)
    initial[form_type] = record
    return form_class(request.user, initial=initial)


@check_auth
def contrib_profile(request):
    context = {
        "letters": Letter.objects.filter(created_by=request.user).order_by("created_date"),
        "people": Person.objects.filter(created_by=request.user).order_by("created_date"),
    }
    return render(request, "contributors/profile.html", context)


class RegistrationView(Dj_Reg):
    form_class = RegistrationForm

    def get_email_context(self, activation_key):
        """
        Returns a dictionary of values to be used as template context when generating the
        activation email.

        :param str activation_key: The activation key for the new user account.
        :rtype: dict

        """
        scheme = "https" if self.request.is_secure() else "http"
        return {
            "scheme": scheme,
            "activation_key": activation_key,
            "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
            "domain": settings.DOMAIN,
        }


class LoginView(DjLoginView):
    form_class = AuthenticationForm


class PasswordResetView(DjPasswordResetView):
    form_class = PasswordResetForm
