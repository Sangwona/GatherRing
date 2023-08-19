from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse

# Create your views here.

def index(request):
    # Authenticated users view the main page
    if request.user.is_authenticated:
        return render(request, "main/layout.html")

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))
