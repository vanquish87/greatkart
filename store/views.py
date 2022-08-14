from django.shortcuts import get_object_or_404, render, redirect

from category.models import Category
from .models import Product, ReviewRating, ProductGallery
from cart.models import CartItem
from cart.views import _cart_id
from .utils import paginationStore
# going to use Q lookup to use "OR" in search
from django.db.models import Q
from django.contrib import messages
from .forms import ReviewForm
from order.models import OrderProduct


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(
            category=categories,
            is_available=True
            ).order_by('id')
        # products = get_list_or_404(Product,
        #  category=categories, is_available=True)

    else:
        products = Product.objects.all().filter(
            is_available=True
            ).order_by('id')

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
        single_product = Product.objects.get(
            category__slug=category_slug,
            slug=product_slug
            )
        # check if already added to the cart or not,
        # cart__cart_id) because of onetoMany
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request),
            product=single_product
            ).exists()
    except Exception as e:
        raise e

    # fix anonymous user error
    if request.user.is_authenticated:
        # check if user has already bought this product
        try:
            orderproduct = OrderProduct.objects.filter(
                                            user=request.user,
                                            product_id=single_product.id
                                            ).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(
                                product_id=single_product.id,
                                status=True
                                )

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(
                                product_id=single_product.id
                                )

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
        }
    return render(request, 'store/product-detail.html', context)


def search(request):
    keyword = ''
    # extract search_query from frontend
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

    # going to use Q lookup to use "OR" in search '|' will say OR
    # using icontains because we don't need case senstivity
    products = Product.objects.filter(
        Q(description__icontains=keyword) |
        Q(product_name__icontains=keyword)
    ).order_by('-created_date')

    product_count = products.count()
    # pagination
    results = 2
    custom_range, paged_products = paginationStore(request, products, results)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'custom_range': custom_range,
        }

    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    # get the previous URL from wehre user came
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # overwriting already submitted review
            review = ReviewRating.objects.get(
                                        user__id=request.user.id,
                                        product__id=product_id
                                        )
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(
                    request,
                    'Thank you! Your review has been updated.'
                    )
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                        request,
                        'Thank you! Your review has been submitted.'
                        )
                return redirect(url)
