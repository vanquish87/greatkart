from urllib import request
from .models import Cart, CartItem
from .views import _cart_id

# it returns the dictionary of all the objects from model
# this will add up all the products n quanities in the cart to show up in navbar
def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[0])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0

    return dict(cart_count=cart_count)