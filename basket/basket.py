from store.models import Product
from decimal import Decimal


class Basket():

    def __init__(self, request):
        self.session = request.session
        basket = self.session.get('session-key')
        if 'session-key' not in request.session:
            basket = self.session['session-key'] = {}
        self.basket = basket

    def add(self, product, qty):
        product_id = product.id

        if product_id not in self.basket:
            self.basket[product_id] = {
                'price': str(product.price), 'qty': int(qty)}

        self.session.modified = True

    def __iter__(self):
        product_ids = self.basket.keys()
        products = Product.products.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            yield item

    def __len__(self):

        return sum(item['qty'] for item in self.basket.values())

    def update(self, product, qty):

        product_id = str(product)
        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
        self.save()

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['qty'] for item in self.basket.values())

    def delete(self, product):

        product_id = str(product)

        if product_id in self.basket:
            del self.basket[product_id]
            print(product_id)
            self.save()

    def save(self):
        self.session.modified = True
