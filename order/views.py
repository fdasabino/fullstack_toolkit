from basket.basket import Basket
from django.http.response import JsonResponse
from django.shortcuts import render

from .models import Order, OrderItem


def add(request):
    """
    Add products found in the basket to the order.
    """

    basket = Basket(request)
    if request.POST.get("action") == "post":

        order_key = request.POST.get("order_key")
        user_id = request.user.id
        baskettotal = basket.get_total_price()

        # Check if order exists
        if not Order.objects.filter(order_key=order_key).exists():
            order = Order.objects.create(
                user_id=user_id,
                full_name="name",
                address1="add1",
                address2="add2",
                total_paid=baskettotal,
                order_key=order_key,
            )
            order_id = order.pk

            for item in basket:
                OrderItem.objects.create(
                    order_id=order_id,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["qty"],
                )

        return JsonResponse({"success": "Return something"})


def payment_confirmation(data):
    """
    Displays an order confirmation setting payment status to true.
    """
    Order.objects.filter(order_key=data).update(billing_status=True)


def user_orders(request):
    """
    Collects all orders with payment status set to true and display to user.
    """
    user_id = request.user.id
    return Order.objects.filter(user_id=user_id).filter(billing_status=True)
