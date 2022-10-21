from django.shortcuts import render
from django.http import HttpResponse
from backdate_form import BackdateForm


def index(request):
    print("INDEX BAY-BEEEE")
    return HttpResponse("<html><body>hi there</body></html>")


# def backdate_form(request):
#     form = BackdateForm
#     if form.is_valid():
#         return
