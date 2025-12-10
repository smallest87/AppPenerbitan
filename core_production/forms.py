from django import forms
from .models import ProductionWorkflow, Order, BookSpecification
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
        fields = ['judul_buku', 'nama_pemesan', 'deadline', 'total_harga', 'status_global']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}), # Agar muncul kalender
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