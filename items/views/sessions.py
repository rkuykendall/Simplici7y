from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
)
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login

from ..forms import (
    UserForm,
)
from django.contrib import messages


def log_out(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
    else:
        form = UserForm()

    return render(request, "signup.html", {"form": form})


def session_create(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")

                next_url = request.GET.get("next", "home")
                return redirect(next_url)

            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(
        request=request, template_name="login.html", context={"login_form": form}
    )


@login_required
def settings(request):
    user = request.user
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
    else:
        form = UserForm(instance=user)

    return render(request, "simple_form.html", {"form": form, "title": "User Settings"})
