from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse

# Create your views here.

def index(request):
    return render(request, "main/index.html")