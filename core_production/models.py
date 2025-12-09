from django.db import models
from django.contrib.auth.models import User

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

# --- 1. Tabel Order ---
class Order(models.Model):
    nomor_order = models.CharField(max_length=20, unique=True)
    judul_buku = models.CharField(max_length=255)
    nama_pemesan = models.CharField(max_length=100)
    deadline = models.DateField()
    status_global = models.CharField(max_length=10, choices=STATUS_GLOBAL, default='BARU')
    total_harga = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    def __str__(self):
        return self.nomor_order

# --- 2. Tabel Spesifikasi ---
class BookSpecification(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='spesifikasi')
    ukuran_buku = models.CharField(max_length=50)
    jenis_sampul = models.CharField(max_length=50, choices=[('SOFT', 'Softcover'), ('HARD', 'Hardcover')])
    laminasi = models.CharField(max_length=50, choices=[('DOFF', 'Doff'), ('GLOSSY', 'Glossy')])
    catatan_teknis = models.TextField(blank=True)

# --- 3. Tabel Workflow ---
class ProductionWorkflow(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='workflow')
    
    # Pre-Press
    status_layout = models.CharField(max_length=10, choices=STATUS_PREPRESS, default='PENDING')
    status_desain = models.CharField(max_length=10, choices=STATUS_PREPRESS, default='PENDING')
    
    # Produksi
    status_cetak = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')
    status_binding = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')
    status_finishing = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')