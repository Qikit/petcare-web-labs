from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Pet
from .forms import PetForm


@login_required
def pet_list(request):
    pets = Pet.objects.filter(owner=request.user).order_by('name')
    return render(request, 'pets/list.html', {'pets': pets})


@login_required
def pet_create(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            return redirect('pet-list')
    else:
        form = PetForm()
    return render(request, 'pets/form.html', {'form': form, 'title': 'Добавить питомца'})


@login_required
def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('pet-list')
    else:
        form = PetForm(instance=pet)
    return render(request, 'pets/form.html', {'form': form, 'title': 'Редактировать питомца'})


@login_required
def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        pet.delete()
        return redirect('pet-list')
    return render(request, 'pets/confirm_delete.html', {'pet': pet})
