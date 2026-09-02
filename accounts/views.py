from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "რეგისტრაცია წარმატებით დასრულდა!")
            return redirect('home')
        else:
            messages.error(request, "რეგისტრაცია ვერ მოხერხდა. გთხოვთ შეამოწმოთ შეყვანილი მონაცემები.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'register_form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"მოგესალმებით, {user.student_name}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "ავტორიზაცია ვერ მოხერხდა. გთხოვთ შეამოწმოთ მონაცემები.")
    else:
        form = CustomAuthenticationForm(request)

    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "თქვენ წარმატებით გამოხვედით სისტემიდან.")
    return redirect('home')

