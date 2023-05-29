from django.shortcuts import render


# Create your views here.
def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)
