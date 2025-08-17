from django.shortcuts import render

from src.viz.util import Stat


def stats(request):
    context = {
        "stats": [Stat("Letters Received", "5004"), Stat("Packages Sent", "1005")]
    }
    return render(request, "stats/stats.html", context)
