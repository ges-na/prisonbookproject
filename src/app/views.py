from functools import wraps
from typing import Callable

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django_registration.backends.activation.views import RegistrationView as Dj_Reg

from src.app.forms import (
    ContribLetterForm,
    ContribPersonForm,
    ContribProblemNoteForm,
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
        if not request.user or not request.user.is_authenticated:
            return redirect("/accounts/login")
        elif not request.user.is_contributor and not request.user.is_staff:
            return redirect("/contrib/not_contributor")

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
        form = ContribLetterForm(request.POST)
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
        form = ContribPersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Person created.")
            return redirect("contrib_person_add")
    else:
        form = ContribPersonForm(request.user)
    return render(request, "contributors/add_person.html", {"form": form})


@check_auth
def contrib_add_problem_note_form(
    request, letter: Letter | None = None, person: Person | None = None
):
    if request.method == "POST":
        form = ContribProblemNoteForm(request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Note added.")
            return redirect("contrib_profile")
    else:
        initial = {}
        if letter_id := request.GET.get("letter"):
            letter = Letter.objects.get(id=letter_id)
            initial["letter"] = letter
        elif person_id := request.GET.get("person"):
            person = Person.objects.get(id=person_id)
            initial["person"] = person
        if (letter and not letter.created_by == request.user) or (
            person and not person.created_by == request.user
        ):
            messages.error(
                request,
                f"You do not have permission to add a note to this {'letter' if letter else 'person'}.",
            )
            return redirect("contrib_profile")
        form = ContribProblemNoteForm(request.user)
    return render(
        request,
        "contributors/add_problem_note.html",
        {"form": form},
    )


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
