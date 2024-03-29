from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from order.models import Order
from order.views import add, user_orders
from store.models import Product

from .forms import RegistrationForm, UserAddressForm, UserEditForm
from .models import Address, Customer
from .tokens import account_activation_token


@login_required
def wishlist(request):
    """
    Returns a list of products saved for later purchase.
    """
    products = Product.objects.filter(users_wishlist=request.user)
    return render(request, "account/user/user_wishlist.html", {"wishlist": products})


@login_required
def add_to_wishlist(request, id):
    """
    Add or remove items from wishlist according to its status.
    """
    product = get_object_or_404(Product, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        messages.info(request, f"{product.title} removed from favorites.")
    else:
        product.users_wishlist.add(request.user)
        messages.info(request, f"{product.title} added to favorites.")
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def dashboard(request):
    """
    Displays the dashboard view.
    """
    orders = user_orders(request)
    return render(request, "account/user/dashboard.html", {"section": "profile", "orders": orders})


@login_required
def edit_details(request):
    """
    Displays edit details page.
    """
    return render(request, "account/user/edit_details.html")


@login_required
def delete_user(request):
    """
    Allows users to delete their account.
    """

    user = Customer.objects.get(name=request.user)
    user.is_active = False
    user.save()
    logout(request)
    messages.info(request, "Account deleted successfully.")
    return redirect("account:delete_confirmation")


def account_register(request):
    """
    Account registration.
    """

    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            return account_register_email(registerForm, request)
    else:
        registerForm = RegistrationForm()
    return render(request, "account/registration/register.html", {"form": registerForm})


def account_register_email(registerForm, request):
    """
    Account registration email, sends an email to the user with an unique identifier.
    """
    user = registerForm.save(commit=False)
    user.email = registerForm.cleaned_data["email"]
    user.set_password(registerForm.cleaned_data["password"])
    user.is_active = False
    user.save()
    current_site = get_current_site(request)
    subject = "Activate your Account"
    message = render_to_string(
        "account/registration/account_activation_email.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )
    user.email_user(subject=subject, message=message)
    return render(request, "account/registration/register_email_confirm.html")


def account_activate(request, uidb64, token):
    """
    Account activation page.
    """

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None
    if user is None or not account_activation_token.check_token(user, token):
        return render(request, "account/registration/activation_invalid.html")

    user.is_active = True
    user.save()
    messages.info(
        request,
        "Account activated successfully. Please log in using your new credentials.",
    )
    return redirect("account:login")


# Addresses
@login_required
def view_address(request):
    """
    Displays all delivery addresses that user have registered.
    """

    addresses = Address.objects.filter(customer=request.user)
    return render(request, "account/user/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    """
    Alow users to add addresses.
    """

    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.customer = request.user
            address_form.save()
            return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address_form = UserAddressForm()
    return render(request, "account/user/edit_addresses.html", {"form": address_form})


@login_required
def edit_address(request, id):
    """
    Allows user to edit an addresses.
    """
    if request.method == "POST":
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, "account/user/edit_addresses.html", {"form": address_form})


@login_required
def delete_address(request, id):
    """
    Allows users to delete an address.
    """
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect("account:addresses")


@login_required
def set_default(request, id):
    """
    Allows user to set an address to default.
    """

    Address.objects.filter(customer=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, customer=request.user).update(default=True)
    messages.info(request, "Default delivery address updated.")
    return redirect("account:addresses")


@login_required
def user_orders(request):
    """
    Displays addresses connected to an specific order.
    """
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
    return render(request, "account/user/user_orders.html", {"orders": orders})
