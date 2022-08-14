from django.shortcuts import render
from store.models import Product, ReviewRating


def home(request):
    '''this is the home
    dsakfhads lsaf dslfasd fsdlajf
    dfsld jgfsld gj'''
    # products = Product.objects.all().filter(is_available=True)
    # products = get_list_or_404(Product, is_available=True)

    products = Product.objects.all().filter(
                            is_available=True
                            ).order_by(
                                'created_date'
                                )

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }

    return render(request, 'home.html', context)

