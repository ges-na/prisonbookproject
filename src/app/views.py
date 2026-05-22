# from backdate_form import BackdateForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from src.app.forms import ContribLetterForm, ContribPersonForm
from src.app.models.letter import Letter
from src.app.models.person import Person


def index(request):
    print("INDEX BAY-BEEEE")
    return HttpResponse("<html><body>hi there</body></html>")


def redirect_to_admin(request):
    return HttpResponseRedirect("/admin")


def contrib_letter_form(request):
    if request.method == "POST":
        if not request.user.is_authenticated or not request.user.is_contributor:
            return redirect("/accounts/login/")
        form = ContribLetterForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect("contrib_letter_add")
    else:
        form = ContribLetterForm()
    return render(request, "contributors/add_letter.html", {"form": form})


def contrib_person_form(request):
    if request.method == "POST":
        if not request.user.is_authenticated or not request.user.is_contributor:
            return redirect("/accounts/login/")
        form = ContribPersonForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect("contrib_person_add")
    else:
        form = ContribPersonForm()
    return render(request, "contributors/add_person.html", {"form": form})


def contrib_profile(request):
    context = {
        "letters": Letter.objects.filter(created_by=request.user).order_by("created_date"),
        "people": Person.objects.filter(created_by=request.user).order_by("created_date"),
    }
    return render(request, "contributors/profile.html", context)


# def backdate_form(request):
#     form = BackdateForm
#     if form.is_valid():
#         return
