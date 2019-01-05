from django import forms as dform
from django.forms import fields, widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------委托合同添加-------------------------#
class AgreeAddForm(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['lending', 'branch', 'agree_typ', 'guarantee_typ', 'agree_copies', 'agree_amount']
        widgets = {'lending': dform.Select(attrs={'class': 'form-control'}),
                   'branch': dform.Select(attrs={'class': 'form-control'}),
                   'agree_typ': dform.Select(attrs={'class': 'form-control'}),
                   'guarantee_typ': dform.Select(attrs={'class': 'form-control'}),
                   'agree_copies': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同份数'}),
                   'agree_amount': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '合同金额（元）'})}


# -----------------------反担保合同添加-------------------------#
class AddCounterForm(dform.ModelForm):  # 反担保合同添加
    class Meta:
        model = models.Counters
        fields = ['counter_typ']
        widgets = {'counter_typ': dform.Select(attrs={'class': 'form-control'})}
