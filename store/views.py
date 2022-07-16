from itertools import product
from math import prod
import re
from django.shortcuts import get_object_or_404, render

from category.models import Category
from .models import Product
from cart.models import CartItem
from cart.views import _cart_id
from .utils import paginationStore

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)

    product_count = products.count()
    # pagination
    results = 3
    custom_range, paged_products = paginationStore(request, products, results)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'custom_range': custom_range,
        }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    single_product = None

    try:
        # using foreign key of Category
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # check if already added to the cart or not, cart__cart_id) because of onetoMany
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        }
    return render(request, 'store/product-detail.html', context)