from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import login, logout

from .forms import RegisterForm, LoginForm

# Create your views here.

def user(request):
    return HttpResponse("Hello, user!")

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if (form.is_valid()):
            login(request, form.get_user())
            return redirect("index")
        else:
            return render(request, "user/login.html", {
            'form': form
        })
    else:
        return render(request, "user/login.html", {
            'form': LoginForm()
        })

def logout_view(request):
    logout(request)
    return redirect("index")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if (form.is_valid()):
            user = form.save()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "user/register.html", {
            'form': form
        })
    else:
        return render(request, "user/register.html", {
            'form': RegisterForm()
        })