from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------放款通知添加-------------------------#
class FormNotifyAdd(dform.ModelForm):
    class Meta:
        model = models.Notify
        fields = ['notify_money', 'notify_date', 'contracts_lease', 'contract_guaranty', 'remark']
        widgets = {
            'notify_money': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '通知金额'}),
            'notify_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contracts_lease': dform.TextInput(attrs={'class': 'form-control'}),
            'contract_guaranty': dform.TextInput(attrs={'class': 'form-control'}),
            'remark': dform.TextInput(attrs={'class': 'form-control'})}


# -----------------------放款添加-------------------------#
class FormProvideAdd(dform.ModelForm):
    class Meta:
        model = models.Provides
        fields = ['provide_typ', 'provide_money', 'provide_date', 'due_date']
