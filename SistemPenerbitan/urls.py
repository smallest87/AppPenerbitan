from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from core_production.views import (
    CustomLoginView, 
    dashboard_admin, 
    dashboard_prepress, 
    dashboard_produksi,
    update_prepress # <--- JANGAN LUPA IMPORT INI
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Halaman Login (Halaman Utama saat web dibuka)
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Halaman Dashboard Divisi
    path('dashboard/admin/', dashboard_admin, name='dash_admin'),
    path('dashboard/pre-press/', dashboard_prepress, name='dash_prepress'),
    path('dashboard/produksi/', dashboard_produksi, name='dash_produksi'),

    # Pre-Press Routes
    path('dashboard/pre-press/', dashboard_prepress, name='dash_prepress'),
    path('dashboard/pre-press/update/<int:workflow_id>/', update_prepress, name='update_prepress'),
]