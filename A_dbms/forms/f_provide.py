from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------风控落实添加-------------------------#
class FormAscertainAdd(dform.ModelForm):
    class Meta:
        model = models.Agrees
        fields = ['agree_state', 'agree_remark']
        widgets = {
            'agree_state': dform.Select(attrs={'class': 'form-control'}),
            'agree_remark': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '落实情况'})}


# -----------------------合同签订-------------------------#
class FormCounterSignAdd(dform.ModelForm):
    class Meta:
        model = models.Counters
        fields = ['counter_state', 'counter_sign_date', 'counter_remark']
        widgets = {
            'counter_state': dform.Select(attrs={'class': 'form-control'}),
            'counter_sign_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'counter_remark': dform.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '签订情况'})}


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
        widgets = {
            'provide_typ': dform.Select(attrs={'class': 'form-control', 'placeholder': '通知金额'}),
            'provide_money': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '放款金额'}),
            'provide_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}


# -----------------------放款添加-------------------------#
class FormRepaymentAdd(dform.ModelForm):
    class Meta:
        model = models.Repayments
        fields = ['repayment_money', 'repayment_date']
        widgets = {
            'repayment_money': dform.NumberInput(attrs={'class': 'form-control', 'placeholder': '还款金额'}),
            'repayment_date': dform.DateInput(attrs={'class': 'form-control', 'type': 'date'})}
