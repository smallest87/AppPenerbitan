from django.contrib import admin
from .models import Order, BookSpecification, ProductionWorkflow

class BookSpecInline(admin.StackedInline):
    model = BookSpecification
    can_delete = False

class WorkflowInline(admin.StackedInline):
    model = ProductionWorkflow
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('nomor_order', 'judul_buku', 'status_global', 'deadline')
    inlines = [BookSpecInline, WorkflowInline]