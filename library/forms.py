from .models import FormStreamYear
from django.forms import ModelForm

class FormStreamYearForm(ModelForm):
    
    class Meta:
        model = FormStreamYear
        fields = ['form_label', 'year']