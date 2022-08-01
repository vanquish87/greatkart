from genericpath import exists
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from cart.models import Cart, CartItem
from store.models import Product, Variation


# Create your views here.
# this is a for setting up a session & as a private function from pep8
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    # making a list of different variation of 1 product
    product_variation = []

    # to get size n color or other for single product
    if request.method == 'POST':
        # color = request.POST['color']
        # size = request.POST['size']
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    try:
        # using _cart_id from session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    # add items to cart or create cart items
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        # check for existing variations in selected cart_item
        for item in cart_item:
            # manytomany relationship called
            # it will make a queryset like color:blue n size:small
            # <QuerySet [<Variation: Yellow>, <Variation: large>]>
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        # import pdb; pdb.set_trace()

        # check if new added variation is in existing variation list
        if product_variation in ex_var_list:
            # increase the cart_item quantity
            # we are finding index value of product_variation that exists
            # in ex_var_list n fing that cart_item
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()

        # check if new added variation is actually new
        elif len(product_variation) > 0:
            item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
                )
            item.variations.clear()
            # to add all product_variation ek saath
            item.variations.add(*product_variation)

            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )

        if len(product_variation) > 0:
            cart_item.variations.clear()
            item.variations.add(*product_variation)

        cart_item.save()

    return redirect('cart')


# for minus button in the cart
def minus_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


# for deleting the item altogether from cart
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()

    return redirect('cart')


def cart(request):
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        # tax n total calculation
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)
