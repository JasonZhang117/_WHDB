from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------合作协议-------------------------#
class FormAgreementAdd(dform.ModelForm):
    class Meta:
        model = models.Agreements
        fields = ['flow_credit', 'flow_limit', 'back_credit', 'back_limit',
                  'credit_date', 'due_date']
        widgets = {
            'flow_credit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '综合授信额度'}),
            'flow_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '单笔额度(综合)'}),
            'back_credit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '保函额度'}),
            'back_limit': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '单笔额度(保函)'}),
            'credit_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
