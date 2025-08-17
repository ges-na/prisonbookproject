from django.shortcuts import render
from django.http import HttpResponse

# from backdate_form import BackdateForm
from django.http import HttpResponseRedirect


def index(request):
    print("INDEX BAY-BEEEE")
    return HttpResponse("<html><body>hi there</body></html>")


def redirect_to_admin(request):
    return HttpResponseRedirect("/admin")


# def backdate_form(request):
#     form = BackdateForm
#     if form.is_valid():
#         return
