from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.trending_products, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('product/<str:model>/', views.product_details, name='product_details'),
    path('recommend/', views.recommended_products, name='recommend'),
    path('apple/', views.apple_products, name='apple'),
    path('samsung/', views.samsung_products, name='samsung'),
    path('xiaomi/', views.xiaomi_products, name='xiaomi'),
    path('search/', views.search, name='search'),
    path('like/<str:model>/', views.like_product, name='like_product'),
]