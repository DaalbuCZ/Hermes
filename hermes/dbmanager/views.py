from django.shortcuts import render, redirect
from .models import TestResultDatabase


def select_database(request):
    if request.method == "POST":
        db_name = request.POST.get("db_name")
        request.session["selected_db"] = db_name
        return redirect("admin:index")
    databases = TestResultDatabase.objects.all()
    return render(request, "select_database.html", {"databases": databases})
