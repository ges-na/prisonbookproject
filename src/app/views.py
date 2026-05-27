# from backdate_form import BackdateForm
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django_registration.backends.activation.views import RegistrationView as Dj_Reg

from src.app.forms import ContribLetterForm, ContribPersonForm, ContribProblemNoteForm
from src.app.models.letter import Letter
from src.app.models.person import Person


def index(request):
    print("INDEX BAY-BEEEE")
    return HttpResponse("<html><body>hi there</body></html>")


def redirect_to_admin(request):
    return HttpResponseRedirect("/admin")


def redirect_to_contrib_profile(request):
    return HttpResponseRedirect("/contrib/profile")


def contrib_logout(request):
    return render(request, "contributors/logout.html")


def contrib_letter_form(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_contributor:
        return redirect("/accounts/login/")
    if request.method == "POST":
        form = ContribLetterForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, "Letter created.")
            return redirect("contrib_letter_add")
    else:
        form = ContribLetterForm()
    return render(request, "contributors/add_letter.html", {"form": form})


def contrib_person_form(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_contributor:
        return redirect("/accounts/login/")
    if request.method == "POST":
        form = ContribPersonForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, "Person created.")
            return redirect("contrib_person_add")
    else:
        form = ContribPersonForm()
    return render(request, "contributors/add_person.html", {"form": form})


def contrib_add_problem_note_form(
    request, letter: Letter | None = None, person: Person | None = None
):
    if not request.user or not request.user.is_authenticated or not request.user.is_contributor:
        return redirect("/accounts/login/")
    if request.method == "POST":
        form = ContribProblemNoteForm(request.POST)
        if form.is_valid():
            form.save(request.user)
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
        form = ContribProblemNoteForm(initial=initial)
    return render(
        request,
        "contributors/add_problem_note.html",
        {"form": form},
    )


def contrib_profile(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_contributor:
        return redirect("/accounts/login/")
    context = {
        "letters": Letter.objects.filter(created_by=request.user).order_by("created_date"),
        "people": Person.objects.filter(created_by=request.user).order_by("created_date"),
    }
    return render(request, "contributors/profile.html", context)


class RegistrationView(Dj_Reg):
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

    def send_activation_email(self, user):
        """
        Given an inactive user account, generates and sends the activation email for that
        account.

        :param django.contrib.auth.models.AbstractUser user: The new user account.
        :rtype: None

        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context["user"] = user
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request,
        )
        # Force subject to a single line to avoid header-injection issues.
        subject = "".join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request,
        )
        breakpoint()
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
