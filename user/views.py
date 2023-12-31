from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from django.http import Http404

from .forms import RegisterForm, LoginForm, EditUserForm
from .models import User
from group.models import Group
from event.models import Event

# Create your views here.
def login_view(request):
    if request.method == "POST":
        loginForm = LoginForm(data=request.POST)
        if (loginForm.is_valid()):
            login(request, loginForm.get_user(), backend='django.contrib.auth.backends.ModelBackend')
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
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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

@login_required
def edit(request, user_id):
    if (request.user.id != user_id):
        raise PermissionDenied
    
    user = get_object_or_404(User, pk=user_id)
    
    if (request.method == "POST"):
        editUserForm = EditUserForm(request.POST, request.FILES, instance=user)
        if editUserForm.is_valid():
            editUserForm.save()
            return redirect("user_profile", user_id=user_id)
        
    else:
        editUserForm = EditUserForm(instance=user)
    
    return render(request, "user/edit.html", {
        "form": editUserForm,
    })

@login_required
def my_group(request, user_id):
    if request.user.id == user_id:
        return render(request, "user/myGroup.html", {
            "my_list": request.user.created_groups.all().order_by("-created_at"),
            "admin_list": request.user.administrating_groups.all().order_by("-created_at"),
            "member_list": request.user.attending_groups.all().order_by("-created_at")
        })
    else:
        raise PermissionDenied
    
@login_required
def my_event(request, user_id):
    if request.user.id == user_id:
        return render(request, "user/myEvent.html", {
            "my_list": request.user.created_events.all().order_by("-start_time"),
            "hosting_list": request.user.hosting_events.all().order_by("-start_time"),
            "attending_list": request.user.attending_events.all().order_by("-start_time")
        })
    else:
        raise PermissionDenied
