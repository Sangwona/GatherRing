from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import login, logout

from .forms import RegisterForm, LoginForm

# Create your views here.

def user(request):
    return HttpResponse("Hello, user!")

def login_view(request):
    if request.method == "POST":
        loginForm = LoginForm(data=request.POST)
        if (loginForm.is_valid()):
            login(request, loginForm.get_user())
            return redirect("index")
        else:
            return render(request, "user/login.html", {
            'form': loginForm
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
        registerForm = RegisterForm(request.POST)
        if (registerForm.is_valid()):
            user = registerForm.save()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "user/register.html", {
            'form': registerForm
        })
    else:
        return render(request, "user/register.html", {
            'form': RegisterForm()
        })