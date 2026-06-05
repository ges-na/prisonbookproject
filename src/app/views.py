from functools import wraps
from typing import Callable

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
    ContribPersonForm,
    ContribProblemNoteForm,
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
def contrib_add_problem_note_form(request):
    if request.method == "POST":
        form = ContribProblemNoteForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Note added.")
        else:
            messages.error(request, "Invalid note.")
        return redirect("contrib_profile")
    else:
        initial = {}
        for note_type, model in {"letter": Letter, "person": Person}.items():
            if record_id := request.GET.get(note_type):
                record = model.objects.get(id=record_id)
                if not record.created_by == request.user:
                    messages.error(
                        request,
                        f"You do not have permission to add a note to this {note_type}.",
                    )
                initial[note_type] = record
        form = ContribProblemNoteForm(request.user, initial=initial)
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


class LoginView(DjLoginView):
    form_class = AuthenticationForm


class PasswordResetView(DjPasswordResetView):
    form_class = PasswordResetForm
