from django.shortcuts import redirect, render, get_object_or_404

from accounts.models import Account, UserProfile
from order.models import Order, OrderProduct
from .forms import RegistrationForm, UserProfileForm, UserForm
# for flashing messages
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from cart.models import Cart, CartItem
from cart.views import _cart_id

import requests


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

            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            # message will be rendered from html + dictionary context
            message = render_to_string('accounts/account-activate.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            # messages.success(request, message)
            # messages.error(request, email)
            # messages.warning(request, mail_subject)
            send_email.send()

            # messages.success(request, 'Thank you for registering with us.
            # We have sent you a verification email to your email address
            # Please verify it.')
            return redirect(
                '/accounts/login/?command=verification&email='+email
                )
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
            try:
                # using _cart_id from session
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                        cart=cart
                        ).exists()
                # saving cart_item via onetoMany relationship with user
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                # Getting the product variations by cart id
                product_variation = []
                for item in cart_item:
                    variation = item.variations.all()
                    product_variation.append(list(variation))

                # Get the cart items from the user to access
                # his product variations
                cart_item = CartItem.objects.filter(user=user)
                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)

                # product_variation = [1, 2, 3, 4, 6]
                # ex_var_list = [4, 6, 3, 5]

                for pr in product_variation:
                    if pr in ex_var_list:
                        index = ex_var_list.index(pr)
                        item_id = id[index]
                        item = CartItem.objects.get(id=item_id)
                        item.quantity += 1
                        item.user = user
                        item.save()
                    else:
                        cart_item = CartItem.objects.filter(cart=cart)
                        for item in cart_item:
                            item.user = user
                            item.save()
            except ValueError:
                pass

            # sets session for user
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            messages.error(request, 'You are now logged in.')
            messages.info(request, 'You are now logged in.')
            messages.warning(request, 'You are now logged in.')

            # this code is for getting user to the next page.. ie checkout page
            # get the previous URL from wehre user came
            url = request.META.get('HTTP_REFERER')
            try:
                # to get query = next=/cart/checkout/
                query = requests.utils.urlparse(url).query
                # to split query into dict for getting
                # {'next': '/cart/checkout/'}
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    # this will redirect user to Website--/cart/checkout/ page
                    return redirect(nextPage)
            except KeyError:
                pass

            return redirect('dashboard')
        else:
            messages.error(request, 'email or password is incorrect')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')


# used to validate token sent on user email
def activate(request, uidb64, token):
    # decode user.id to get user from Account
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # user exist n token is valid against user using check_token
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Congratulations! Your account is activated.'
            )
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by(
                            '-created_at'
                            ).filter(
                                user_id=request.user.id,
                                is_ordered=True
                                )
    orders_count = orders.count()
    context = {
     'orders_count': orders_count
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset-password-email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request,
                'Password reset email has been sent to your email address.'
                )
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # using session to save uid
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(
                        user=request.user,
                        is_ordered=True
                        ).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my-orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        # because we are updating existing user that's why instance
        user_form = UserForm(request.POST, instance=request.user)
        # do define OnetoOne relationship we used instance of userprofile
        profile_form = UserProfileForm(
                                request.POST,
                                request.FILES,
                                instance=userprofile
                                )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit-profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # django inbuild check_password method
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change-password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change-password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change-password')
    return render(request, 'accounts/change-password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order-detail.html', context)
