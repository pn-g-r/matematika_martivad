from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    StaffRegistrationForm,
    PasswordResetPhoneForm,
    PasswordResetOTPForm,
    PasswordResetConfirmForm,
    RegistrationOTPForm,
)
from .models import CustomUser
from .password_reset import (
    SESSION_PHONE,
    SESSION_USER_ID,
    GENERIC_OTP_SENT_MESSAGE,
    clear_password_reset_session,
    mask_phone,
    request_otp,
    verify_otp,
)
from .registration_verification import (
    SESSION_REGISTRATION_DATA,
    SESSION_REGISTRATION_PHONE,
    clear_registration_session,
    mask_phone as mask_registration_phone,
    request_registration_otp,
    verify_registration_otp,
)

def staff_register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('home')

    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.PhoneOrUsernameModelBackend')
            messages.success(request, f"ადმინისტრატორის ანგარიში ({user.username}) წარმატებით შეიქმნა!")
            return redirect('/admin/')
        else:
            messages.error(request, "ადმინის რეგისტრაცია ვერ მოხერხდა. გთხოვთ შეამოწმოთ მონაცემები.")
    else:
        form = StaffRegistrationForm()

    return render(request, 'registration/staff_register.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            registration_data = {
                'student_name': form.cleaned_data['student_name'],
                'phone_number': phone,
                'parent_name': form.cleaned_data['parent_name'],
                'grade': form.cleaned_data['grade'],
                'book_author': form.cleaned_data['book_author'],
                'password': form.cleaned_data['password1'],
            }
            request.session[SESSION_REGISTRATION_DATA] = registration_data
            request.session[SESSION_REGISTRATION_PHONE] = phone
            ok, err = request_registration_otp(phone)
            if ok:
                messages.success(request, f"SMS კოდი გამოგეგზავნათ ნომერზე {mask_registration_phone(phone)}")
                return redirect('register_verify')
            else:
                messages.error(request, err or "SMS გაგზავნა ვერ მოხერხდა. სცადეთ თავიდან.")
        else:
            messages.error(request, "რეგისტრაცია ვერ მოხერხდა. გთხოვთ შეამოწმოთ შეყვანილი მონაცემები.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'register_form': form})


def register_verify_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    reg_data = request.session.get(SESSION_REGISTRATION_DATA)
    phone = request.session.get(SESSION_REGISTRATION_PHONE)
    if not reg_data or not phone:
        messages.error(request, "გთხოვთ თავიდან შეავსოთ რეგისტრაციის ფორმა.")
        return redirect('register')

    if request.method == 'POST':
        form = RegistrationOTPForm(request.POST)
        if form.is_valid():
            ok, err = verify_registration_otp(phone, form.cleaned_data['code'])
            if ok:
                if CustomUser.objects.filter(phone_number=phone).exists():
                    messages.error(request, "ამ ნომრით მომხმარებელი უკვე დარეგისტრირებულია.")
                    clear_registration_session(request)
                    return redirect('login')

                user = CustomUser.objects.create_user(
                    username=phone,
                    phone_number=phone,
                    password=reg_data['password'],
                    student_name=reg_data.get('student_name', ''),
                    parent_name=reg_data.get('parent_name', ''),
                    grade=reg_data.get('grade', ''),
                    book_author=reg_data.get('book_author', ''),
                )
                clear_registration_session(request)
                login(request, user, backend='accounts.backends.PhoneOrUsernameModelBackend')
                messages.success(request, "რეგისტრაცია და ტელეფონის დადასტურება წარმატებით დასრულდა!")
                return redirect('home')
            messages.error(request, err)
        else:
            messages.error(request, "გთხოვთ შეამოწმოთ SMS კოდი.")
    else:
        form = RegistrationOTPForm()

    return render(request, 'registration/register_verify.html', {
        'form': form,
        'masked_phone': mask_registration_phone(phone),
    })


@require_POST
def register_resend_otp_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    phone = request.session.get(SESSION_REGISTRATION_PHONE)
    if not phone:
        messages.error(request, "გთხოვთ თავიდან შეავსოთ რეგისტრაციის ფორმა.")
        return redirect('register')

    ok, err = request_registration_otp(phone)
    if ok:
        messages.success(request, "ახალი SMS კოდი გამოგეგზავნათ.")
    else:
        messages.error(request, err)
    return redirect('register_verify')

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


def password_reset_request_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = PasswordResetPhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            ok, err = request_otp(phone)
            if ok:
                request.session[SESSION_PHONE] = phone
                request.session.pop(SESSION_USER_ID, None)
                messages.success(request, GENERIC_OTP_SENT_MESSAGE)
                return redirect('password_reset_verify')
            messages.error(request, err)
        else:
            messages.error(request, "გთხოვთ შეამოწმოთ ტელეფონის ნომერი.")
    else:
        form = PasswordResetPhoneForm()

    return render(request, 'registration/password_reset.html', {'form': form})


def password_reset_verify_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    phone = request.session.get(SESSION_PHONE)
    if not phone:
        messages.error(request, "ჯერ შეიყვანეთ ტელეფონის ნომერი.")
        return redirect('password_reset')

    if request.method == 'POST':
        form = PasswordResetOTPForm(request.POST)
        if form.is_valid():
            user, err = verify_otp(phone, form.cleaned_data['code'])
            if user:
                request.session[SESSION_USER_ID] = user.pk
                messages.success(request, "კოდი სწორია. შეიყვანეთ ახალი პაროლი.")
                return redirect('password_reset_confirm')
            messages.error(request, err)
        else:
            messages.error(request, "გთხოვთ შეამოწმოთ SMS კოდი.")
    else:
        form = PasswordResetOTPForm()

    return render(request, 'registration/password_reset_verify.html', {
        'form': form,
        'masked_phone': mask_phone(phone),
    })


@require_POST
def password_reset_resend_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    phone = request.session.get(SESSION_PHONE)
    if not phone:
        messages.error(request, "ჯერ შეიყვანეთ ტელეფონის ნომერი.")
        return redirect('password_reset')

    ok, err = request_otp(phone)
    if ok:
        messages.success(request, GENERIC_OTP_SENT_MESSAGE)
    else:
        messages.error(request, err)
    return redirect('password_reset_verify')


def password_reset_confirm_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    user_id = request.session.get(SESSION_USER_ID)
    phone = request.session.get(SESSION_PHONE)
    if not user_id or not phone:
        messages.error(request, "ჯერ დაადასტურეთ SMS კოდი.")
        return redirect('password_reset')

    user = CustomUser.objects.filter(pk=user_id, phone_number=phone, is_active=True).first()
    if user is None:
        clear_password_reset_session(request)
        messages.error(request, "სესია ვადაგასულია. სცადეთ თავიდან.")
        return redirect('password_reset')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(user, request.POST)
        if form.is_valid():
            form.save()
            clear_password_reset_session(request)
            login(request, user, backend='accounts.backends.PhoneOrUsernameModelBackend')
            messages.success(request, "პაროლი წარმატებით შეიცვალა.")
            return redirect('home')
        messages.error(request, "გთხოვთ შეამოწმოთ პაროლი.")
    else:
        form = PasswordResetConfirmForm(user)

    return render(request, 'registration/password_reset_confirm.html', {'form': form})

