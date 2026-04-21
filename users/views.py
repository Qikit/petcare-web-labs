from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import LoginForm, RegisterForm, ProfileForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему')
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url or 'index')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    appointments = request.user.appointments.select_related(
        'doctor__user', 'pet', 'service'
    ).order_by('-date')[:10]
    pets = request.user.pets.all()
    return render(request, 'profile/index.html', {
        'appointments': appointments,
        'pets': pets,
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profile/edit.html', {'form': form})
