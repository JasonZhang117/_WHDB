from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------代偿添加-------------------------#
class FormCompensatoryAdd(dform.ModelForm):
    class Meta:
        model = models.Compensatories
        fields = ['compensatory_date', 'compensatory_capital', 'compensatory_interest']
        widgets = {
            'compensatory_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'compensatory_capital': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '代偿本金金额'}),
            'compensatory_interest': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '代偿利息金额'})}
