from django.urls import path
from .import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path(
        'resetpassword_validate/<uidb64>/<token>/',
        views.resetpassword_validate,
        name='resetpassword_validate'
        ),
    path('resetPassword/', views.resetPassword, name='resetPassword'),


    path('my-orders/', views.my_orders, name='my-orders'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('change-password/', views.change_password, name='change-password'),
    path(
        'order-detail/<int:order_id>/',
        views.order_detail,
        name='order-detail'
        ),
]
