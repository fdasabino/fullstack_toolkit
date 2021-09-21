from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .basket import Basket
from store.views import Product


def basket_summary(request):
    return render(request, 'store/basket/summary.html')


def basket_add(request):  # sourcery skip: inline-immediately-returned-variable
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty)
        response = JsonResponse({'qty': product_qty})
        return response