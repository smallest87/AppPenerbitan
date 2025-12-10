from django import forms
from .models import ProductionWorkflow, Order, BookSpecification, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class PrePressForm(forms.ModelForm):
    class Meta:
        model = ProductionWorkflow
        # Kita batasi field apa saja yang boleh diedit oleh Layouter/Desainer
        fields = ['status_layout', 'file_layout_final', 'status_desain', 'file_cover_final']
        
        # Sedikit styling agar form terlihat bagus (Bootstrap class)
        widgets = {
            'status_layout': forms.Select(attrs={'class': 'form-select'}),
            'status_desain': forms.Select(attrs={'class': 'form-select'}),
            'file_layout_final': forms.FileInput(attrs={'class': 'form-control'}),
            'file_cover_final': forms.FileInput(attrs={'class': 'form-control'}),
        }

class StaffSignUpForm(UserCreationForm):
    DIVISI_CHOICES = [
        ('Pre-Press', 'Tim Layout & Desain'),
        ('Produksi', 'Tim Produksi (Cetak/Binding)'),
    ]
    
    divisi = forms.ChoiceField(choices=DIVISI_CHOICES) # Widget diatur otomatis di bawah

    class Meta:
        model = User
        fields = ['username', 'email']

    # --- TAMBAHAN PENTING: OTOMATISASI STYLE ---
    def __init__(self, *args, **kwargs):
        super(StaffSignUpForm, self).__init__(*args, **kwargs)
        # Loop semua field untuk menyuntikkan class Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'
            field.help_text = '' # Hapus help text yang mengganggu (opsional)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            nama_group = self.cleaned_data['divisi']
            group = Group.objects.get(name=nama_group)
            user.groups.add(group)
            user.is_staff = True 
            user.save()
        return user
    
# Form untuk Edit Data Utama Order
class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        # Tambahkan 'status_pembayaran' dan 'jumlah_bayar' ke dalam fields
        fields = ['judul_buku', 'nama_pemesan', 'deadline', 'total_harga', 'status_global', 'status_pembayaran', 'jumlah_bayar']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm'

# Form untuk Edit Spesifikasi Buku
class BookSpecEditForm(forms.ModelForm):
    class Meta:
        model = BookSpecification
        fields = ['ukuran_buku', 'jenis_sampul', 'laminasi', 'catatan_teknis']
        widgets = {
            'catatan_teknis': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm'

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        # Kita sertakan 'nomor_order' karena ini wajib di awal
        fields = ['nomor_order', 'judul_buku', 'nama_pemesan', 'deadline', 'total_harga', 'status_global']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition shadow-sm'

# Form untuk Edit Data User (Khusus Admin)
class UserEditForm(forms.ModelForm):
    # Field khusus untuk memilih Group/Divisi
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'h-24'}), # Tampilan list select
        label="Divisi / Jabatan"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'groups']
        help_texts = {
            'username': '', # Hapus help text bawaan yang panjang
            'is_active': 'Hilangkan centang untuk memblokir akses login user ini.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Styling Tailwind
        for field_name, field in self.fields.items():
            # Checkbox butuh style beda
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500 border-gray-300'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm'

# Form untuk Edit Profil Tambahan
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nama_tampilan', 'jenis_kelamin', 'tanggal_lahir', 'foto_profil']
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date'}),
            'jenis_kelamin': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Styling Tailwind standar
            if field_name != 'foto_profil': # File input punya style beda dikit biasanya
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm'