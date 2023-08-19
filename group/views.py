from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def group(request):
    return HttpResponse("Hello, group!")