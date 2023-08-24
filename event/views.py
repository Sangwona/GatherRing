from django.shortcuts import render
from django.http import HttpResponse
from .forms import CreateEventForm

# Create your views here.

def event(request):
    return HttpResponse("Hello, event!")

def create(request):
    if request.method == "POST":
        createEventForm = CreateEventForm(request.POST)
        if createEventForm.is_valid():
            event = createEventForm.save(commit=False)
            event.creator = request.user
            event.save()

            return render(request, "event/profile.html", {
                'form_data': createEventForm.cleaned_data
            })
        else:
            return render(request, "event/create.html", {
                "form": createEventForm
            })
    else:
        return render(request, "event/create.html", {
            "form": CreateEventForm(),
        }) 