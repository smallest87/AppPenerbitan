from django import forms
from .models import ProductionWorkflow

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