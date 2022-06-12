from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    print("INDEX BAY-BEEEE")
    return HttpResponse("<html><body>hi there</body></html>")

# Create your views here.
