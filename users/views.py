from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth import logout

from .models import MyUser
from pgs.models import PgListing

# Email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


# ---------------------- LOGIN ---------------------------
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user:
            auth.login(request, user)

            if user.is_owner:
                if not PgListing.objects.filter(owner=user).exists():
                    return redirect('pg_register')
                return HttpResponse("Owner Dashboard")

            return redirect('home')

        messages.error(request, "Invalid Login Credentials")
        return redirect('user_login')

    return render(request, 'users/login.html')


# ---------------------- SIGNUP (CHOICE PAGE) ---------------------------
def signup(request):
    return render(request, 'users/signup.html')



# ---------------------- CLIENT REGISTER ---------------------------
def client_register(request):
    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        password = request.POST.get('create_password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('client_register')

        if MyUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('client_register')

        if MyUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('client_register')

        if MyUser.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already in use")
            return redirect('client_register')

        user = MyUser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            gender=gender,
            date_of_birth=dob,
            address=address,
            is_owner=False
        )
        user.set_password(password)
        user.save()

        # EMAIL SEND
        current_site = get_current_site(request)
        mail_subject = "Activate Your Account"

        message = render_to_string('users/account_varification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        try:
            EmailMessage(mail_subject, message, to=[email]).send()
        except:
            messages.error(request, "Email sending failed")

        messages.success(request, "Verification email sent!")
        return redirect('/user/login/?command=verification&email=' + email)

    return render(request, 'users/clients/client_register.html')



# ---------------------- OWNER REGISTER ---------------------------
def owner_register(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        aadhar = request.POST.get('aadhar')
        password = request.POST.get('create_password')
        confirm_password = request.POST.get('confirm_password')
        image = request.FILES.get('image')
        address = request.POST.get('address')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('owner_register')

        if MyUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('owner_register')

        if MyUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('owner_register')

        if MyUser.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists")
            return redirect('owner_register')

        if aadhar and MyUser.objects.filter(aadhar_card=aadhar).exists():
            messages.error(request, "Aadhar already in use")
            return redirect('owner_register')

        user = MyUser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            gender=gender,
            date_of_birth=dob,
            aadhar_card=aadhar,
            profile_image=image,
            address=address,
            is_owner=True
        )
        user.set_password(password)
        user.save()

        # EMAIL SEND
        current_site = get_current_site(request)
        mail_subject = "Activate Your Owner Account"

        message = render_to_string('users/account_varification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        EmailMessage(mail_subject, message, to=[email]).send()

        return redirect('/user/login/?command=verification&email=' + email)

    return render(request, 'users/owners/register.html')



# ---------------------- EMAIL ACTIVATION ---------------------------
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MyUser.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully!")
        return redirect("user_login")

    messages.error(request, "Invalid or expired link")
    return redirect("user_login")



# ---------------------- LOGOUT ---------------------------
def user_logout(request):
    logout(request)
    return redirect("home")



# ---------------------- FORGOT PASSWORD ---------------------------
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not MyUser.objects.filter(email=email).exists():
            messages.error(request, "Account does not exist")
            return redirect('forgotPassword')

        user = MyUser.objects.get(email=email)

        current_site = get_current_site(request)
        email_subject = "Reset Your Password"

        message = render_to_string('users/reset_password_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        EmailMessage(email_subject, message, to=[email]).send()
        messages.success(request, "Password reset link sent to your email")
        return redirect('user_login')

    return render(request, 'users/forgotPassword.html')



# ---------------------- VALIDATE RESET LINK ---------------------------
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MyUser.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        request.session['email'] = user.email
        return redirect('resetPassword')

    messages.error(request, "Link expired")
    return redirect('user_login')



# ---------------------- RESET PASSWORD ---------------------------
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('resetPassword')

        uid = request.session.get('uid')
        user = MyUser.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        messages.success(request, "Password changed successfully")
        return redirect('user_login')

    return render(request, 'users/resetPassword.html', {
        'email': request.session.get('email')
    })



# ---------------------- TERMS ---------------------------
def terms_conditions(request):
    return render(request, 'users/terms&conditions.html')


# ---------------------- DASHBOARD: MY PROFILE ---------------------------
def my_profile(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        phone = request.POST.get('phone', user.phone)
        gender = request.POST.get('gender', user.gender)
        dob = request.POST.get('date_of_birth', user.date_of_birth)
        address = request.POST.get('address', user.address)
        city = request.POST.get('city', user.city)
        state = request.POST.get('state', user.state)
        pin_code = request.POST.get('pin_code', user.pin_code)
        profile_image = request.FILES.get('profile_image')

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.gender = gender
        if dob:
            user.date_of_birth = dob
        user.address = address
        user.city = city
        user.state = state
        user.pin_code = pin_code
        if profile_image:
            user.profile_image = profile_image

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('my_profile')

    context = {'user_obj': user, 'page': 'profile'}
    return render(request, 'users/dashboard/my_profile.html', context)


# ---------------------- DASHBOARD: MY BOOKINGS ---------------------------
def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    # Placeholder: integrate with your booking model later
    bookings = []
    context = {'bookings': bookings, 'page': 'bookings'}
    return render(request, 'users/dashboard/my_bookings.html', context)


# ---------------------- DASHBOARD: SETTINGS ---------------------------
def settings_view(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    user = request.user

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "All password fields are required")
            return redirect('settings')

        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect")
            return redirect('settings')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect('settings')

        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect('settings')

        user.set_password(new_password)
        user.save()
        auth.login(request, user)  # Re-login to keep session active
        messages.success(request, "Password changed successfully!")
        return redirect('settings')

    context = {'user_obj': user, 'page': 'settings'}
    return render(request, 'users/dashboard/settings.html', context)


# ---------------------- DASHBOARD: HELP & SUPPORT ---------------------------
def help_support(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    faqs = [
        {'q': 'How do I search for PGs?', 'a': 'Use the search bar on the home page to filter PGs by location, price range, and amenities.'},
        {'q': 'How do I book a PG?', 'a': 'Click on a PG listing and use the contact form to reach out to the owner directly.'},
        {'q': 'Can I change my profile information?', 'a': 'Yes, visit My Profile to update your personal details anytime.'},
        {'q': 'How do I reset my password?', 'a': 'Click "Forgot Password" on the login page and follow the email instructions.'},
        {'q': 'Is my data secure?', 'a': 'Yes, we use secure encryption and do not share your data with third parties.'},
    ]

    context = {'faqs': faqs, 'page': 'help'}
    return render(request, 'users/dashboard/help_support.html', context)

