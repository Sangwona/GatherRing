from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import Http404

from .forms import RegisterForm, LoginForm
from .models import User

# Create your views here.
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
    
def profile(request, user_id):
    try: 
        profile_user = User.objects.get(pk=user_id)
        return render(request, "user/profile.html", {
            "profile_user": profile_user
        })
    except User.DoesNotExist:
        raise Http404("User does not exist")
