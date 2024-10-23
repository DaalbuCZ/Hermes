from django.shortcuts import render, redirect
# from .forms import TestResultForm
from .models import TestResult

# def add_test_result(request):
#     if request.method == "POST":
#         form = TestResultForm(request.POST)
#         if form.is_valid():
#             test_result = form.save(commit=False)
#             test_result.user = request.user  # Assign the current user
#             test_result.save()
#             return redirect('test_results')  # Redirect to a page showing test results
#     else:
#         form = TestResultForm()
#     return render(request, 'add_test_result.html', {'form': form})

def test_results(request):
    results = TestResult.objects.all()
    return render(request, 'results.html', {'results': results})

def index(request):
    return render(request, 'index.html')
