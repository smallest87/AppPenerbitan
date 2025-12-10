from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

# --- Status Choices ---
STATUS_GLOBAL = [
    ('BARU', 'Order Baru'),
    ('PROSES', 'Dalam Pengerjaan'),
    ('SIAP', 'Siap Diambil/Dikirim'),
    ('BATAL', 'Dibatalkan'),
]

STATUS_PREPRESS = [
    ('PENDING', 'Menunggu'),
    ('PROSES', 'Sedang Dikerjakan'),
    ('ACC', 'Final / ACC'),
]

STATUS_PRODUKSI = [
    ('ANTRI', 'Dalam Antrian'),
    ('PROSES', 'Sedang Dikerjakan'),
    ('SELESAI', 'Selesai'),
]

# Tambahkan Pilihan Status Bayar
STATUS_BAYAR = [
    ('BELUM', '❌ Belum Bayar'),
    ('DP', '⚠️ Down Payment (DP)'),
    ('LUNAS', '✅ Lunas'),
]

# --- 1. Tabel Utama: Order ---
class Order(models.Model):
    nomor_order = models.CharField(max_length=20, unique=True, help_text="Contoh: PO-001")
    judul_buku = models.CharField(max_length=255)
    nama_pemesan = models.CharField(max_length=100)
    deadline = models.DateField()
    status_global = models.CharField(max_length=10, choices=STATUS_GLOBAL, default='BARU')
    
    # --- UPDATE SEKTOR KEUANGAN ---
    total_harga = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    # Kolom Baru:
    status_pembayaran = models.CharField(max_length=10, choices=STATUS_BAYAR, default='BELUM')
    jumlah_bayar = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text="Total uang yang sudah diterima")

    # Logika Hitung Sisa (Virtual Field)
    @property
    def sisa_tagihan(self):
        return self.total_harga - self.jumlah_bayar

    def __str__(self):
        return f"{self.nomor_order} - {self.judul_buku}"

# --- 2. Tabel Spesifikasi ---
# --- TAMBAHAN BARU: Pilihan Ukuran Buku Standar ---
UKURAN_CHOICES = [
    ('A5', 'A5 (14.8 x 21 cm) - Standar Buku Ajar/Novel'),
    ('B5', 'B5 (17.6 x 25 cm) - Akademik/Jurnal'),
    ('A4', 'A4 (21 x 29.7 cm) - Majalah/Modul'),
    ('13x19', '13 x 19 cm - Novel Komersial/Fiksi'),
    ('14x20', '14 x 20 cm - Standar Umum'),
    ('15x23', '15.5 x 23 cm - Standar UNESCO'),
    ('CUSTOM', 'Custom / Ukuran Khusus'),
]

# --- 2. Tabel Spesifikasi ---
class BookSpecification(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='spesifikasi')
    
    # UPDATE DI SINI: Tambahkan choices=UKURAN_CHOICES
    ukuran_buku = models.CharField(
        max_length=20, 
        choices=UKURAN_CHOICES, 
        default='A5'
    )
    
    jenis_sampul = models.CharField(max_length=50, choices=[('SOFT', 'Softcover'), ('HARD', 'Hardcover')], default='SOFT')
    laminasi = models.CharField(max_length=50, choices=[('DOFF', 'Doff'), ('GLOSSY', 'Glossy')], default='DOFF')
    catatan_teknis = models.TextField(blank=True, help_text="Instruksi khusus untuk produksi")

    def __str__(self):
        return f"Spek: {self.order.nomor_order}"

# --- 3. Tabel Workflow ---
class ProductionWorkflow(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='workflow')
    
    # Pre-Press
    status_layout = models.CharField(max_length=10, choices=STATUS_PREPRESS, default='PENDING')
    file_layout_final = models.FileField(upload_to='uploads/layout/', blank=True, null=True)
    
    status_desain = models.CharField(max_length=10, choices=STATUS_PREPRESS, default='PENDING')
    file_cover_final = models.FileField(upload_to='uploads/cover/', blank=True, null=True)
    
    # Produksi
    status_cetak = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')
    status_binding = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')
    status_finishing = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')

    def __str__(self):
        return f"Workflow: {self.order.nomor_order}"

# =========================================================
# LOGIKA "SAFE SIGNAL" (SOLUSI INTI)
# =========================================================
@receiver(post_save, sender=Order)
def create_related_tables(sender, instance, created, **kwargs):
    # Logika: "Cek dulu, kalau belum ada baru buat"
    
    # 1. Handle Spesifikasi
    try:
        instance.spesifikasi
    except ObjectDoesNotExist:
        BookSpecification.objects.create(order=instance)

    # 2. Handle Workflow
    try:
        instance.workflow
    except ObjectDoesNotExist:
        ProductionWorkflow.objects.create(order=instance)

# --- TAMBAHAN BARU: MODEL PROFIL USER ---
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    nama_tampilan = models.CharField(max_length=100, blank=True, help_text="Nama yang akan muncul di dashboard")
    jenis_kelamin = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    tanggal_lahir = models.DateField(null=True, blank=True)
    foto_profil = models.ImageField(upload_to='uploads/profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

# --- UPDATE SIGNAL: BUAT PROFIL OTOMATIS SAAT USER DIBUAT ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Logika Safe Signal (Cek dulu sebelum buat)
    try:
        instance.profile
    except ObjectDoesNotExist:
        UserProfile.objects.create(user=instance)

# --- 4. Tabel Log Aktivitas (Audit Trail) ---
class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs')
    aktivitas = models.CharField(max_length=255) # Contoh: "Menginput Order PO-001"
    waktu = models.DateTimeField(auto_now_add=True) # Otomatis mencatat waktu sekarang

    def __str__(self):
        return f"{self.user.username} - {self.aktivitas}"
    
