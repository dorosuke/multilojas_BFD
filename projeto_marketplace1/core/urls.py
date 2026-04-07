from django.urls import path

from .views import (
    ApiRootView,
    HealthCheckView,
    buyer_dashboard_page,
    forgot_password_page,
    home_page,
    login_page,
    profile_page,
    product_page,
    register_page,
    search_page,
    seller_dashboard_page,
    store_page,
)

urlpatterns = [
    path('', ApiRootView.as_view(), name='api-root'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('front/', home_page, name='front-home'),
    path('front/busca/', search_page, name='front-search'),
    path('front/loja/<slug:slug>/', store_page, name='front-store'),
    path('front/produto/<slug:slug>/', product_page, name='front-product'),
    path('front/vendedor/', seller_dashboard_page, name='front-seller-dashboard'),
    path('front/comprador/', buyer_dashboard_page, name='front-buyer-dashboard'),
    path('front/login/', login_page, name='front-login'),
    path('front/cadastro/', register_page, name='front-register'),
    path('front/recuperar-senha/', forgot_password_page, name='front-forgot-password'),
    path('front/perfil/', profile_page, name='front-profile'),
]
