from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import ReviewForm
from doctors.models import Doctor


@login_required
def review_create(request, doctor_pk):
    doctor = get_object_or_404(Doctor, pk=doctor_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.doctor = doctor
            review.save()
            return HttpResponseRedirect(
                reverse('doctor-detail', kwargs={'pk': doctor_pk})
            )
    else:
        form = ReviewForm()

    return render(request, 'reviews/form.html', {'form': form, 'doctor': doctor})
