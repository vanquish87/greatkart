import email
from django.shortcuts import redirect, render

from accounts.models import Account
from .forms import RegistrationForm
# for flashing messages
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # creating username from email
            username = email.split('@')[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            # phone_number will be saved later as it is not in create_user
            user.phone_number = phone_number
            user.save()
            messages.success(request, 'User account was created!')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # this check password against username in database
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            # sets session for user
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'email or password is incorrect')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')
