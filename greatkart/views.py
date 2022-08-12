from django.shortcuts import render
from store.models import Product


def home(request):
    '''this is the home
    dsakfhads lsaf dslfasd fsdlajf
    dfsld jgfsld gj'''
    products = Product.objects.all().filter(is_available=True)
    # products = get_list_or_404(Product, is_available=True)

    context = {'products': products}
    return render(request, 'home.html', context)
