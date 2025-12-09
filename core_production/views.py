from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.utils import timezone # Tambahan untuk logika warna deadline
from .models import Order, ProductionWorkflow # <--- Pastikan ProductionWorkflow di-import
from .forms import PrePressForm # <--- IMPORT FORM YANG BARU DIBUAT

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
    # Cek akses
    if not (request.user.is_superuser or request.user.groups.filter(name='Pre-Press').exists()):
        return redirect('login')
    
    # Tampilkan order yang belum selesai Layout/Desain-nya
    # Kita filter yang status globalnya masih BARU atau PROSES
    orders = Order.objects.filter(status_global__in=['BARU', 'PROSES']).order_by('-id')
    
    context = {
        'orders': orders,
        'user': request.user
    }
    return render(request, 'dashboard_prepress.html', context)

@login_required
def update_prepress(request, workflow_id):
    # Ambil data workflow spesifik
    workflow = get_object_or_404(ProductionWorkflow, id=workflow_id)
    
    if request.method == 'POST':
        # Masukkan data dari form ke database
        form = PrePressForm(request.POST, request.FILES, instance=workflow)
        if form.is_valid():
            form.save()
            return redirect('dash_prepress') # Kembali ke dashboard setelah save
    else:
        # Jika baru buka halaman, tampilkan isian yang sekarang
        form = PrePressForm(instance=workflow)

    return render(request, 'form_prepress_update.html', {'form': form, 'order': workflow.order})

@login_required
def dashboard_produksi(request):
    # Cek: Hanya user 'Produksi' atau 'Superuser' yang boleh masuk
    # Kita gunakan filter groups__name agar lebih fleksibel
    if not (request.user.is_superuser or request.user.groups.filter(name='Produksi').exists()):
        return redirect('login')
    
    # Ambil data: Urutkan berdasarkan ID (Terbaru)
    # Kita ambil semua order agar terlihat di tabel
    orders = Order.objects.select_related('spesifikasi', 'workflow').all().order_by('-id')
    
    context = {
        'orders': orders,
        'user': request.user
    }
    return render(request, 'dashboard_produksi.html', context)