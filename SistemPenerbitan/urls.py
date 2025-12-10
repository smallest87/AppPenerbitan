from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Import SEMUA views yang sudah kita buat
from core_production.views import (
    CustomLoginView, 
    logout_view,
    signup_view,            # Fitur Tambah Staff
    dashboard_admin, 
    dashboard_prepress, 
    dashboard_produksi,
    create_order,           # Fitur Input Order Baru
    edit_order_detail,      # Fitur Edit Detail
    update_prepress,        # Fitur Update Desainer
    update_production_status, # Fitur Update Operator
    manage_users,           # Fitur Kelola User
    edit_user,              # Fitur Edit User
    view_system_logs,        # Fitur Lihat Log Sistem
    print_spk,              # Fitur Cetak SPK
    print_invoice          # Fitur Cetak Invoice
)

urlpatterns = [
    # 1. Admin Django Bawaan
    path('admin/', admin.site.urls),
    
    # 2. Otentikasi (Login/Logout/Signup)
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),

    # 3. Dashboard Admin & Manajemen Order
    path('dashboard/admin/', dashboard_admin, name='dash_admin'),
    path('order/create/', create_order, name='create_order'),          # URL Create
    path('order/edit/<int:order_id>/', edit_order_detail, name='edit_order'), # URL Edit

    # 4. Dashboard Pre-Press (Desainer)
    path('dashboard/pre-press/', dashboard_prepress, name='dash_prepress'),
    path('dashboard/pre-press/update/<int:workflow_id>/', update_prepress, name='update_prepress'),
    
    # 5. Dashboard Produksi (Operator)
    path('dashboard/produksi/', dashboard_produksi, name='dash_produksi'),
    path('dashboard/produksi/update/<int:workflow_id>/', update_production_status, name='update_produksi'),

    # URL MANAJEMEN USER
    path('users/', manage_users, name='manage_users'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),

    path('logs/', view_system_logs, name='system_logs'),

    path('order/print/spk/<int:order_id>/', print_spk, name='print_spk'),
    path('order/print/invoice/<int:order_id>/', print_invoice, name='print_invoice'),
]

# Konfigurasi agar file upload (Media) bisa dibuka di browser
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)