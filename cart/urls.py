from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path(
        'add-cart/<int:product_id>/',
        views.add_cart,
        name='add-cart'
        ),
    path(
        'minus-cart/<int:product_id>/<int:cart_item_id>/',
        views.minus_cart,
        name='minus-cart'
        ),
    path(
        'remove-cart/<int:product_id>/<int:cart_item_id>/',
        views.remove_cart,
        name='remove-cart'
        ),
    path('checkout/', views.checkout, name='checkout'),
]
