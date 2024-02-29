from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.models import User, auth

# For Email sending 
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User  
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.http import HttpResponse

from django.conf import settings

from .tokens import account_activation_token


from django.template.loader import render_to_string

from django.core.mail import send_mail

from django.template.loader import get_template

from .models import Profile

# Create your views here.
def home(request):
    return render(request, 'core/home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)


    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # check if email is not same
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used. Try to Login.")
                return redirect('signup')
            
            # check if username is not same
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken.")
                return redirect('signup')
            
            else:
                # create user
                user = User.objects.create_user(username=username, email=email, password=password)
                print(user.username)

                # create profile for new user
                Profile.objects.create(user=user)

                user.is_active = False
                user.save()

                # Send email to user
                status = send_verification_email(request, user, email)

                if status:
                    messages.success(request, 'Please check your e-mail!')
                else:
                    messages.success(request, 'Please try after some time! Failed to send mail')

                return redirect('home')
        else:
            messages.info(request, "Password Not Matching.")
            return redirect('signup')

    context = {}
    return render(request, "core/signup.html", context)


def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None

    if user is not None:
        if default_token_generator.check_token(user, token):
            # Token is valid
            user.is_active = True
            user.save()
            messages.success(request, "Thank you for your email confirmation. Now you can login your account. 👍")
            return redirect("login")
        else:
            # token is invalid 
            return HttpResponse("The verification link is invalid.😞")
    else:  
        return HttpResponse('User does not exists!')



def login(request):
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if (user.is_active):
                auth.login(request, user)
                if request.GET.get('next', '') != '':
                    return redirect(request.GET.get('next'))
                return redirect('profile', request.user.username)
            else:
                messages.info(request, 'Please Verify Your Email!')
                return redirect('login')

        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')

    return render(request, "core/login.html")


def logout(request):
    auth.logout(request)
    return redirect('login')

def profile(request, username):
    return render(request, 'core/profile.html')

def send_verification_email(request, user, email):
    try:
        current_site = get_current_site(request)

        subject = 'verification code from website'
        from_email = settings.EMAIL_HOST_USER

        body = render_to_string('core/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        to_email = email
        email = EmailMessage(subject=subject, body=body, from_email=from_email, to=[to_email])
        email.send()

        print(f'E-mail has been sent to {to_email}')

        return True
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred while sending the email: {str(e)}")

        # Return False or any failure indicator if needed
        return False