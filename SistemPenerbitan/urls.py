from django.contrib import admin
from django.urls import path
from django.conf import settings # <--- Tambahan
from django.conf.urls.static import static # <--- Tambahan
from core_production.views import (
    CustomLoginView, 
    dashboard_admin, 
    dashboard_prepress, 
    dashboard_produksi,
    update_prepress,
    logout_view,
    update_production_status,
    signup_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/admin/', dashboard_admin, name='dash_admin'),
    path('dashboard/pre-press/', dashboard_prepress, name='dash_prepress'),
    path('dashboard/pre-press/update/<int:workflow_id>/', update_prepress, name='update_prepress'),

    path('dashboard/produksi/', dashboard_produksi, name='dash_produksi'),
    # URL Baru untuk Operator klik tombol update
    path('dashboard/produksi/update/<int:workflow_id>/', update_production_status, name='update_produksi'),

    path('signup/', signup_view, name='signup'),
]

# Tambahkan baris ajaib ini agar file upload bisa dibuka di browser
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)