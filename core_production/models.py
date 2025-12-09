from django.db import models
from django.contrib.auth.models import User

# --- Status Choices (Pilihan Status) ---
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

# --- 1. Tabel Utama: Order ---
class Order(models.Model):
    nomor_order = models.CharField(max_length=20, unique=True, help_text="Contoh: PO-001")
    judul_buku = models.CharField(max_length=255)
    nama_pemesan = models.CharField(max_length=100)
    deadline = models.DateField()
    
    # Status Utama & Keuangan
    status_global = models.CharField(max_length=10, choices=STATUS_GLOBAL, default='BARU')
    total_harga = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    def __str__(self):
        return f"{self.nomor_order} - {self.judul_buku}"

# --- 2. Tabel Spesifikasi (Detail Teknis) ---
class BookSpecification(models.Model):
    # Relasi OneToOne: 1 Order hanya punya 1 Spesifikasi
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='spesifikasi')
    
    ukuran_buku = models.CharField(max_length=50)
    jenis_sampul = models.CharField(max_length=50, choices=[('SOFT', 'Softcover'), ('HARD', 'Hardcover')])
    laminasi = models.CharField(max_length=50, choices=[('DOFF', 'Doff'), ('GLOSSY', 'Glossy')])
    catatan_teknis = models.TextField(blank=True, help_text="Instruksi khusus untuk produksi")

    def __str__(self):
        return f"Spek: {self.order.nomor_order}"

# --- 3. Tabel Workflow (Tracking Progress) ---
class ProductionWorkflow(models.Model):
    # Relasi OneToOne: 1 Order hanya punya 1 Workflow
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='workflow')
    
    # --- Divisi Pre-Press (Layout & Desain) ---
    status_layout = models.CharField(max_length=10, choices=STATUS_PREPRESS, default='PENDING')
    file_layout_final = models.FileField(upload_to='uploads/layout/', blank=True, null=True)
    
    status_desain = models.CharField(max_length=10, choices=STATUS_PREPRESS, default='PENDING')
    file_cover_final = models.FileField(upload_to='uploads/cover/', blank=True, null=True)
    
    # --- Divisi Produksi (Fisik) ---
    status_cetak = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')
    status_binding = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')
    status_finishing = models.CharField(max_length=10, choices=STATUS_PRODUKSI, default='ANTRI')

    def __str__(self):
        return f"Workflow: {self.order.nomor_order}"