from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.utils import timezone # Tambahan untuk logika warna deadline
from .models import Order 

# --- 1. Custom Login View ---
class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Produksi').exists():
            return '/dashboard/produksi/'
        elif user.groups.filter(name='Pre-Press').exists():
            return '/dashboard/pre-press/'
        else:
            return '/dashboard/admin/'

# --- 2. Dashboard Views (Controller) ---

@login_required
def dashboard_admin(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Penerima Order').exists()):
        return redirect('login') 
    
    # PERBAIKAN DI SINI:
    # Mengubah .order_by('-tanggal_masuk') menjadi .order_by('-id')
    # '-id' artinya urutkan dari ID terbesar (paling baru) ke terkecil
    orders = Order.objects.select_related('spesifikasi', 'workflow').all().order_by('-id')
    
    context = {
        'orders': orders,
        'user': request.user,
        'now': timezone.now().date() # Agar indikator merah "Terlambat" berfungsi
    }
    return render(request, 'dashboard_admin.html', context)

@login_required
def dashboard_prepress(request):
    return render(request, 'dashboard_prepress.html')

@login_required
def dashboard_produksi(request):
    return render(request, 'dashboard_produksi.html')