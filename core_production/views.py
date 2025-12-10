from .forms import PrePressForm, StaffSignUpForm, OrderEditForm, BookSpecEditForm, OrderCreateForm, UserEditForm, UserProfileForm
from .models import Order, UserProfile, ProductionWorkflow, SystemLog # <--- Pastikan ProductionWorkflow di-import
from .utils import render_to_pdf
from django.utils import timezone # Tambahan untuk logika warna deadline
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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

            # --- TAMBAHKAN CATATAN INI ---
            SystemLog.objects.create(
                user=request.user,
                aktivitas=f"Update Progres Desain: {workflow.order.judul_buku}"
            )
            # -----------------------------

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

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def update_production_status(request, workflow_id):
    # Hanya orang produksi yang boleh akses
    if not (request.user.is_superuser or request.user.groups.filter(name='Produksi').exists()):
        return redirect('login')

    if request.method == 'POST':
        workflow = get_object_or_404(ProductionWorkflow, id=workflow_id)
        
        # Ambil jenis proses yang mau diupdate dari tombol yang diklik
        process_type = request.POST.get('process_type') # cetak/binding/finishing
        new_status = request.POST.get('new_status') # PROSES/SELESAI
        
        if process_type == 'cetak':
            workflow.status_cetak = new_status
        elif process_type == 'binding':
            workflow.status_binding = new_status
        elif process_type == 'finishing':
            workflow.status_finishing = new_status
            
            # Jika finishing selesai, update juga status global Order jadi 'SIAP'
            if new_status == 'SELESAI':
                workflow.tanggal_selesai_produksi = timezone.now()
                workflow.order.status_global = 'SIAP'
                workflow.order.save()
        
        workflow.save()

        # --- TAMBAHKAN CATATAN INI (Taruh sebelum return) ---
        pesan_log = f"Produksi ({process_type.upper()}) -> {new_status}: {workflow.order.judul_buku}"
        SystemLog.objects.create(user=request.user, aktivitas=pesan_log)
        # -----------------------------
        
    return redirect('dash_produksi')

@login_required # <--- Wajib login dulu
def signup_view(request):
    # HANYA SUPERUSER YANG BOLEH AKSES
    if not request.user.is_superuser:
        return redirect('login') # Atau redirect ke dashboard mereka sendiri

    if request.method == 'POST':
        form = StaffSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- PERUBAHAN DI SINI ---
            # KITA HAPUS: login(request, user)  <-- Hapus ini agar Admin tidak ter-logout
            
            # Beri notifikasi sukses (Opsional, tapi bagus)
            # messages.success(request, f"Staff {user.username} berhasil ditambahkan!")
            
            return redirect('dash_admin') # Kembali ke Dashboard Admin setelah buat akun
    else:
        form = StaffSignUpForm()
    
    return render(request, 'signup.html', {'form': form})

@login_required
def edit_order_detail(request, order_id):
    # 1. Cek Permission (Hanya Admin/Penerima Order)
    if not (request.user.is_superuser or request.user.groups.filter(name='Penerima Order').exists()):
        return redirect('login')

    # 2. Ambil Data
    order = get_object_or_404(Order, id=order_id)
    # Gunakan 'related_name' spesifikasi dari models.py
    spec = order.spesifikasi 

    if request.method == 'POST':
        # Masukkan data POST ke kedua form
        form_order = OrderEditForm(request.POST, instance=order)
        form_spec = BookSpecEditForm(request.POST, instance=spec)

        if form_order.is_valid() and form_spec.is_valid():
            form_order.save()
            form_spec.save()

            # --- TAMBAHKAN CATATAN INI ---
            SystemLog.objects.create(
                user=request.user,
                aktivitas=f"Update Detail & Spek Order: {order.nomor_order}"
            )
            # -----------------------------

            return redirect('dash_admin') # Kembali ke dashboard setelah save
    else:
        # Isi form dengan data yang sudah ada
        form_order = OrderEditForm(instance=order)
        form_spec = BookSpecEditForm(instance=spec)

    context = {
        'form_order': form_order,
        'form_spec': form_spec,
        'order': order
    }
    return render(request, 'edit_order.html', context)

@login_required
def create_order(request):
    # Cek Permission
    if not (request.user.is_superuser or request.user.groups.filter(name='Penerima Order').exists()):
        return redirect('login')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()

            # --- TAMBAHKAN CATATAN INI ---
            SystemLog.objects.create(
                user=request.user,
                aktivitas=f"Input Order Baru: {order.nomor_order} ({order.judul_buku})"
            )
            # -----------------------------

            # PENTING: Sinyal otomatis sudah membuatkan Spesifikasi & Workflow kosong.
            # Kita langsung lempar user ke halaman EDIT untuk melengkapi data tersebut.
            return redirect('edit_order', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'create_order.html', {'form': form})

# 1. View Daftar User
@login_required
def manage_users(request):
    # HANYA SUPERUSER
    if not request.user.is_superuser:
        return redirect('dash_admin')

    users = User.objects.all().order_by('id')
    return render(request, 'user_list.html', {'users': users})

# 2. View Edit User
@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dash_admin')

    user_obj = get_object_or_404(User, id=user_id)
    
    # Pastikan profil ada (Safe Guard untuk user lama)
    if not hasattr(user_obj, 'profile'):
        UserProfile.objects.create(user=user_obj)

    if request.method == 'POST':
        form_user = UserEditForm(request.POST, instance=user_obj)
        # Perhatikan request.FILES untuk upload foto
        form_profile = UserProfileForm(request.POST, request.FILES, instance=user_obj.profile)
        
        if form_user.is_valid() and form_profile.is_valid():
            form_user.save()
            form_profile.save()
            return redirect('manage_users')
    else:
        form_user = UserEditForm(instance=user_obj)
        form_profile = UserProfileForm(instance=user_obj.profile)

    context = {
        'form_user': form_user,
        'form_profile': form_profile, # Kirim form profil ke template
        'user_obj': user_obj
    }
    return render(request, 'user_edit.html', context)

@login_required
def view_system_logs(request):
    # Hanya Superuser yang boleh lihat log
    if not request.user.is_superuser:
        return redirect('dash_admin')
    
    # Ambil 100 log terakhir, urutkan dari yang paling baru
    logs = SystemLog.objects.select_related('user').all().order_by('-waktu')[:100]
    
    return render(request, 'system_log.html', {'logs': logs})

@login_required
def print_spk(request, order_id):
    # SPK = Surat Perintah Kerja (Untuk Internal)
    # Tidak boleh ada harga di sini
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
        'type': 'SPK'
    }
    return render_to_pdf('pdf/spk_template.html', context)

@login_required
def print_invoice(request, order_id):
    # Invoice = Tagihan (Untuk Eksternal/Klien)
    # Harus ada detail harga
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
        'type': 'INVOICE'
    }
    return render_to_pdf('pdf/invoice_template.html', context)